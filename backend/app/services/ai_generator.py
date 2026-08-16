"""
AI Content Generation Service for Semester OS using Groq API.
Supports multi-key pool rotation, rate-limit failover, and multi-model fallback
(Llama 3.3 70B -> Llama 3.1 8B Instant -> Mixtral 8x7B -> Gemma 2 9B).
"""
import json
import httpx
import itertools
from typing import Optional, List, Dict, Any
from app.core.config import settings

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]


class GroqAIGenerator:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, keys_pool: Optional[List[str]] = None):
        if keys_pool:
            self.keys = [k.strip() for k in keys_pool if k and len(k.strip()) > 5]
        elif api_key:
            self.keys = [api_key.strip()]
        else:
            self.keys = settings.get_groq_keys()

        self._key_cycle = itertools.cycle(self.keys) if self.keys else None
        self.model = model or settings.AI_MODEL or "llama-3.3-70b-versatile"

    def is_configured(self) -> bool:
        return bool(self.keys and len(self.keys) > 0)

    def _get_next_key(self) -> Optional[str]:
        if not self.keys:
            return None
        if self._key_cycle:
            return next(self._key_cycle)
        return self.keys[0]

    async def _call_groq(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> str:
        if not self.is_configured():
            raise ValueError("Groq API Key is not configured. Please provide GROQ_API_KEY in .env or request.")

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = "Unknown error"

        for model_candidate in models_to_try:
            for _ in range(max(len(self.keys), 1)):
                current_key = self._get_next_key()
                headers = {
                    "Authorization": f"Bearer {current_key}",
                    "Content-Type": "application/json",
                }

                payload: Dict[str, Any] = {
                    "model": model_candidate,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 4096,
                }

                if json_mode:
                    payload["response_format"] = {"type": "json_object"}

                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        res = await client.post(GROQ_ENDPOINT, headers=headers, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            return data["choices"][0]["message"]["content"]
                        elif res.status_code == 429:
                            last_error = f"Rate limit on {model_candidate} (key ...{current_key[-6:]}): {res.text}"
                            # If daily limit exceeded on this model, break key loop and try next fallback model
                            if "tokens per day" in res.text.lower() or "tpd" in res.text.lower():
                                break
                            continue
                        else:
                            err_text = res.text
                            try:
                                err_json = res.json()
                                err_text = err_json.get("error", {}).get("message", res.text)
                            except Exception:
                                pass
                            last_error = f"Groq API Error ({res.status_code}): {err_text}"
                except Exception as exc:
                    last_error = str(exc)

        raise RuntimeError(f"All Groq models and keys failed. Last error: {last_error}")

    async def generate_academic_notes(
        self,
        course_code: str,
        subject_name: str,
        unit_number: int,
        unit_name: str,
        topic_name: str,
    ) -> str:
        system_prompt = (
            "You are an elite university computer science professor and technical author. "
            "Write comprehensive, crystal-clear, highly educational academic study notes formatted in Markdown. "
            "Include theoretical intuition, precise definitions, complete code/query snippets, real-world relevance, "
            "common misconceptions, and key takeaways for university semester exams."
        )

        user_prompt = f"""
Please generate comprehensive academic notes for the following syllabus topic:

- Subject: {course_code} — {subject_name}
- Unit: Unit {unit_number}: {unit_name}
- Topic: {topic_name}

Structure the notes with the following Markdown sections:
# {topic_name}
## 1. Conceptual Overview & Intuition
(Clear definition, motivation, real-world context)

## 2. Core Mechanics & Architecture
(How it works under the hood, key rules, diagrams or flow in text/ascii if applicable)

## 3. Implementation & Code Examples
(Clean, runnable code in Java/SQL/JavaScript/Python depending on the subject, with line-by-line explanation)

## 4. Key Properties & Trade-offs
(Time/Space complexity, advantages vs disadvantages, comparison tables if relevant)

## 5. Common Pitfalls & Exam Traps
(Frequent bugs, misconceptions, edge cases)

## 6. High-Yield Exam & Viva Summary
(Bullet points of what professors frequently ask in midterms and finals)
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return await self._call_groq(messages, temperature=0.2)

    async def generate_topic_questions(
        self,
        course_code: str,
        subject_name: str,
        unit_number: int,
        unit_name: str,
        topic_name: str,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are a computer science examination specialist. Create rigorous, high-quality multiple choice questions, "
            "code output prediction questions, and debugging questions strictly aligned with the specified subject syllabus. "
            "Output MUST be valid JSON with a 'questions' array. Each question must have: "
            "'question_text', 'question_type' ('MCQ', 'OUTPUT_PREDICTION', 'DEBUGGING'), 'difficulty' ('EASY', 'MEDIUM', 'HARD'), "
            "'options' (array of 4 items with 'text' and 'is_correct'), and a detailed 'explanation'."
        )

        user_prompt = f"""
Generate {count} high-quality examination questions for:
- Subject: {course_code} ({subject_name})
- Unit {unit_number}: {unit_name}
- Topic: {topic_name}

Format the response strictly as a JSON object matching this schema:
{{
  "questions": [
    {{
      "question_text": "Detailed question text...",
      "question_type": "MCQ",
      "difficulty": "MEDIUM",
      "explanation": "Thorough explanation of the correct answer and why other options are incorrect.",
      "options": [
        {{"text": "Option A text", "is_correct": true}},
        {{"text": "Option B text", "is_correct": false}},
        {{"text": "Option C text", "is_correct": false}},
        {{"text": "Option D text", "is_correct": false}}
      ]
    }}
  ]
}}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        content = await self._call_groq(messages, temperature=0.3, json_mode=True)
        try:
            parsed = json.loads(content)
            return parsed.get("questions", [])
        except Exception:
            return []

    async def generate_coding_problem(
        self,
        course_code: str,
        unit_number: int,
        topic_name: str,
    ) -> Optional[Dict[str, Any]]:
        lang = "JAVA"
        if course_code == "CAP206":
            lang = "SQL"
        elif course_code == "CAP135":
            lang = "JAVASCRIPT"
        elif course_code in ["CAB213", "CAB114"]:
            lang = "PYTHON"

        system_prompt = (
            "You are a coding challenge creator. Generate a hands-on programming exercise with starter template, "
            "clear requirements, example inputs/outputs, and validation hints. "
            "Output must be valid JSON matching the specified schema."
        )

        user_prompt = f"""
Generate a coding problem in {lang} for:
- Subject: {course_code}
- Unit: {unit_number}
- Topic: {topic_name}

Return a JSON object:
{{
  "title": "Problem Title",
  "language": "{lang}",
  "difficulty": "MEDIUM",
  "description": "Problem statement and requirements...",
  "starter_code": "starter template code...",
  "expected_output": "expected stdout or result...",
  "hints": "Helpful hint...",
  "examples": "Example usage..."
}}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        content = await self._call_groq(messages, temperature=0.3, json_mode=True)
        try:
            return json.loads(content)
        except Exception:
            return None
