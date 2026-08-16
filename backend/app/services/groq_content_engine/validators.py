"""
Strict Academic Content Validators & Centralized Cross-Worker Duplicate Detection.

Enforces:
- Exact option counts (4 options per standard MCQ)
- Exactly 1 correct answer per MCQ
- Balanced Markdown code fences
- Prohibited AI placeholder filtering
- Normalized fingerprint collision avoidance
"""
import re
import hashlib
import threading
import logging
from typing import Dict, Any, Tuple, List, Optional, Set

logger = logging.getLogger("ContentValidator")

PROHIBITED_SUBSTRINGS = [
    "lorem ipsum",
    "todo",
    "placeholder",
    "as an ai",
    "as a language model",
    "ai-generated",
    "insert example",
    "insert code here",
    "unknown topic",
    "[insert",
    "<insert",
    "option a is correct",
    "option 1 is correct",
    "none of the above (correct)",
]


class ContentValidator:
    """Validates structural and academic integrity of LLM generated output."""

    @staticmethod
    def _contains_prohibited_text(text: str) -> Optional[str]:
        lower = text.lower()
        for phrase in PROHIBITED_SUBSTRINGS:
            if phrase in lower:
                return phrase
        return None

    @classmethod
    def validate_mcq(cls, q: Dict[str, Any], topic_name: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate a single MCQ dictionary.
        Returns (is_valid, reason, sanitized_mcq_dict).
        """
        if not isinstance(q, dict):
            return False, "MCQ payload is not a JSON object", {}

        question_text = str(q.get("question_text") or "").strip()
        if len(question_text) < 15:
            return False, f"Question text too short ({len(question_text)} chars; min 15)", {}

        bad_phrase = cls._contains_prohibited_text(question_text)
        if bad_phrase:
            return False, f"Question text contains prohibited boilerplate ('{bad_phrase}')", {}

        # Validate options array
        options_raw = q.get("options")
        if not isinstance(options_raw, list) or len(options_raw) != 4:
            return False, f"MCQ must have exactly 4 options; received {len(options_raw) if isinstance(options_raw, list) else 'non-list'}", {}

        cleaned_options = [str(opt).strip() for opt in options_raw]
        if any(len(opt) < 1 for opt in cleaned_options):
            return False, "MCQ contains empty option string", {}

        # Ensure no identical duplicate options within the same question
        unique_opts = set(opt.lower() for opt in cleaned_options)
        if len(unique_opts) != 4:
            return False, f"MCQ has duplicate options ({len(unique_opts)} unique out of 4)", {}

        for opt in cleaned_options:
            bad_opt = cls._contains_prohibited_text(opt)
            if bad_opt:
                return False, f"Option contains prohibited boilerplate ('{bad_opt}')", {}

        # Validate correct index / answer
        correct_idx = q.get("correct_index")
        if correct_idx is None or not isinstance(correct_idx, int) or not (0 <= correct_idx <= 3):
            # Check if options are objects with 'is_correct'
            return False, f"Invalid or missing correct_index (must be integer 0-3; got {correct_idx})", {}

        # Validate explanation
        explanation = str(q.get("explanation") or "").strip()
        if len(explanation) < 15:
            return False, f"Explanation too short ({len(explanation)} chars; min 15)", {}

        bad_exp = cls._contains_prohibited_text(explanation)
        if bad_exp:
            return False, f"Explanation contains prohibited boilerplate ('{bad_exp}')", {}

        # Validate difficulty
        difficulty = str(q.get("difficulty") or "MEDIUM").upper()
        if difficulty not in ["EASY", "MEDIUM", "HARD"]:
            difficulty = "MEDIUM"

        sanitized = {
            "question_text": question_text,
            "options": [
                {"option_text": cleaned_options[i], "is_correct": (i == correct_idx), "sort_order": i}
                for i in range(4)
            ],
            "correct_index": correct_idx,
            "explanation": explanation,
            "difficulty": difficulty,
        }

        return True, "Valid", sanitized

    @classmethod
    def validate_note(cls, content: str, topic_name: str) -> Tuple[bool, str, str]:
        """
        Validate academic digital textbook note content.
        Returns (is_valid, reason, sanitized_content).
        """
        if not content or not isinstance(content, str):
            return False, "Note content is empty or invalid type", ""

        cleaned = content.strip()
        if len(cleaned) < 300:
            return False, f"Note content too short ({len(cleaned)} chars; min 300 for academic depth)", ""

        bad_phrase = cls._contains_prohibited_text(cleaned)
        if bad_phrase:
            return False, f"Note contains prohibited boilerplate text ('{bad_phrase}')", ""

        # Validate balanced code fences (```)
        code_fence_count = cleaned.count("```")
        if code_fence_count % 2 != 0:
            return False, f"Unbalanced Markdown code blocks ({code_fence_count} backtick triples found)", ""

        # Verify topic title alignment
        title_lower = topic_name.lower().strip()
        content_lower = cleaned.lower()
        
        # Split multi-word topic to check at least one primary keyword is present
        topic_words = [w for w in re.findall(r"\w+", title_lower) if len(w) > 3]
        if topic_words and not any(w in content_lower for w in topic_words):
            return False, f"Note does not mention core keywords for topic '{topic_name}'", ""

        return True, "Valid", cleaned


class DuplicateDetector:
    """
    Thread-safe shared duplicate detection across concurrent worker pools.
    Uses normalized token set hashing to catch exact and near-verbatim duplicate questions.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._fingerprints: Set[str] = set()
        self._prevented_count: int = 0

    @staticmethod
    def _normalize(text: str) -> str:
        # Strip code blocks and non-alphanumeric chars
        text_clean = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        text_clean = re.sub(r"[^a-zA-Z0-9\s]", "", text_clean.lower())
        tokens = sorted([t for t in text_clean.split() if len(t) > 2])
        return " ".join(tokens)

    def _hash(self, text: str) -> str:
        norm = self._normalize(text)
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    def preload_existing(self, question_texts: List[str]) -> int:
        """Pre-populate fingerprints from existing database questions."""
        with self._lock:
            for q in question_texts:
                if q and len(q) > 10:
                    fp = self._hash(q)
                    self._fingerprints.add(fp)
            logger.info(f"DuplicateDetector loaded {len(self._fingerprints)} existing question fingerprints.")
            return len(self._fingerprints)

    def is_duplicate(self, question_text: str) -> bool:
        """Check if question is already registered."""
        fp = self._hash(question_text)
        with self._lock:
            return fp in self._fingerprints

    def register_if_unique(self, question_text: str) -> bool:
        """
        Atomically check and register a new question fingerprint.
        Returns True if unique and registered; False if duplicate.
        """
        fp = self._hash(question_text)
        with self._lock:
            if fp in self._fingerprints:
                self._prevented_count += 1
                return False
            self._fingerprints.add(fp)
            return True

    @property
    def duplicates_prevented_count(self) -> int:
        with self._lock:
            return self._prevented_count
