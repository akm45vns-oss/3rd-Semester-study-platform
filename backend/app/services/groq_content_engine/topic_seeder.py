"""
Semester OS — Topic-by-Topic Resumable Academic Content Seeding Engine.

Core Invariants:
1. Generation unit is strictly ONE TOPIC.
2. Note MUST be generated, validated, and saved to database BEFORE MCQs for that topic are generated.
3. Small MCQ batches (5–10 per request); only missing questions are generated.
4. Persistent, crash-proof state (groq_seeding_state.json) survives any restart.
5. Idempotent: Skips topics that already meet database targets.
6. 5-Key round-robin rotation with rate-limit cooldown and failover.
7. Zero modification to existing user data.
"""
import os
import re
import json
import time
import asyncio
import logging
import httpx
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import AsyncSessionLocal, create_tables
from app.models.curriculum import Subject, Unit, Topic
from app.models.practice import Question, QuestionOption, QuestionType, Difficulty, PracticeAttempt
from app.models.progress import Note, TopicProgress, Mistake, RevisionItem
from app.models.user import User
from app.seed.curriculum_data import CURRICULUM, validate_curriculum
from app.services.groq_content_engine.key_manager import GroqKeyManager, AllKeysUnavailableError, KeyStatus
from app.services.groq_content_engine.validators import ContentValidator, DuplicateDetector

logger = logging.getLogger("TopicContentSeeder")

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


class TopicJobState(str, Enum):
    PENDING = "PENDING"
    GENERATING_NOTE = "GENERATING_NOTE"
    VALIDATING_NOTE = "VALIDATING_NOTE"
    NOTE_COMPLETE = "NOTE_COMPLETE"
    GENERATING_MCQ = "GENERATING_MCQ"
    VALIDATING_MCQ = "VALIDATING_MCQ"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    RETRY_REQUIRED = "RETRY_REQUIRED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


@dataclass
class TopicTask:
    topic_identifier: str  # e.g. "CAP392-U01-T001"
    subject_code: str      # e.g. "CAP392"
    subject_name: str      # e.g. "Java Programming"
    unit_number: int       # e.g. 1
    unit_name: str         # e.g. "Introduction"
    topic_name: str        # e.g. "Java program structure"
    target_mcqs: int = 5
    
    # State tracking
    state: TopicJobState = TopicJobState.PENDING
    note_status: str = "PENDING"  # PENDING, SAVED, FAILED
    note_key: Optional[str] = None
    note_attempts: int = 0
    
    mcq_status: str = "PENDING"   # PENDING, SAVED, FAILED
    mcq_count_saved: int = 0
    mcq_key: Optional[str] = None
    mcq_attempts: int = 0
    
    error_message: Optional[str] = None
    last_updated: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopicTask":
        c = dict(data)
        c["state"] = TopicJobState(c["state"])
        return cls(**c)


class TopicContentSeeder:
    """
    Topic-by-Topic Resumable Content Seeder with persistent state and 5-key Groq support.
    """

    def __init__(
        self,
        state_file_path: str = "groq_seeding_state.json",
        max_workers: int = 5,
        target_mcqs_per_topic: int = 5,
        model_name: Optional[str] = None,
    ):
        self.state_file_path = state_file_path
        self.max_workers = max_workers
        self.target_mcqs_per_topic = target_mcqs_per_topic
        self.model_name = model_name or getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        
        self.key_manager = GroqKeyManager()
        self.duplicate_detector = DuplicateDetector()
        self.tasks: Dict[str, TopicTask] = {}
        
        self._state_lock = asyncio.Lock()
        self.load_state()

    def save_state(self) -> None:
        """Atomically persist state dictionary to disk."""
        try:
            temp_path = f"{self.state_file_path}.tmp"
            data = {t_id: task.to_dict() for t_id, task in self.tasks.items()}
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if os.path.exists(self.state_file_path):
                os.replace(temp_path, self.state_file_path)
            else:
                os.rename(temp_path, self.state_file_path)
        except Exception as e:
            logger.error(f"Failed saving state file {self.state_file_path}: {e}")

    def load_state(self) -> None:
        """Load state checkpoint if present on disk."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = {t_id: TopicTask.from_dict(d) for t_id, d in data.items()}
                logger.info(f"Loaded {len(self.tasks)} topic states from {self.state_file_path}.")
            except Exception as e:
                logger.warning(f"Could not parse state file {self.state_file_path}: {e}")

    async def initialize_tasks_and_audit_db(self, db: AsyncSession) -> None:
        """
        Build deterministic task tree from curriculum, audit existing DB content,
        and mark existing completed topics as COMPLETE.
        """
        # 1. Preload question fingerprints from DB
        q_res = await db.execute(select(Question.question_text).where(Question.is_active == True))
        all_q_texts = [r[0] for r in q_res.fetchall()]
        self.duplicate_detector.preload_existing(all_q_texts)

        # 2. Build Topic DB map: (course_code, unit_num, topic_name) -> Topic model
        topic_db_map: Dict[Tuple[str, int, str], Topic] = {}
        top_res = await db.execute(
            select(Topic)
            .join(Unit, Topic.unit_id == Unit.id)
            .join(Subject, Unit.subject_id == Subject.id)
        )
        for t in top_res.scalars().all():
            u = await db.get(Unit, t.unit_id)
            s = await db.get(Subject, u.subject_id) if u else None
            if s and u:
                topic_db_map[(s.course_code.upper(), u.unit_number, t.name.lower().strip())] = t

        # 3. Populate tasks deterministic list
        topic_counter = 1
        for subj in CURRICULUM:
            code = subj["course_code"].upper()
            s_name = subj["name"]
            for unit in subj.get("units", []):
                u_num = unit["unit_number"]
                u_name = unit["name"]
                for top in unit.get("topics", []):
                    top_name = top["name"] if isinstance(top, dict) else str(top)
                    t_identifier = f"{code}-U{u_num:02d}-T{topic_counter:03d}"

                    if t_identifier not in self.tasks:
                        self.tasks[t_identifier] = TopicTask(
                            topic_identifier=t_identifier,
                            subject_code=code,
                            subject_name=s_name,
                            unit_number=u_num,
                            unit_name=u_name,
                            topic_name=top_name,
                            target_mcqs=self.target_mcqs_per_topic,
                        )

                    task = self.tasks[t_identifier]
                    topic_counter += 1

                    # Check DB for existing Note and MCQs (Idempotency Check)
                    db_topic = topic_db_map.get((code, u_num, top_name.lower().strip()))
                    if db_topic:
                        # Check note
                        note_stmt = select(func.count(Note.id)).where(Note.topic_id == db_topic.id)
                        has_note = ((await db.execute(note_stmt)).scalar() or 0) > 0

                        # Check questions
                        q_stmt = select(func.count(Question.id)).where(
                            Question.topic_id == db_topic.id,
                            Question.is_active == True,
                        )
                        mcq_count = (await db.execute(q_stmt)).scalar() or 0

                        if has_note:
                            task.note_status = "SAVED"
                        task.mcq_count_saved = mcq_count

                        if has_note and mcq_count >= task.target_mcqs:
                            task.state = TopicJobState.COMPLETE
                            task.mcq_status = "SAVED"
                        elif has_note:
                            task.state = TopicJobState.NOTE_COMPLETE
                        else:
                            if task.state not in [TopicJobState.FAILED, TopicJobState.MANUAL_REVIEW_REQUIRED]:
                                task.state = TopicJobState.PENDING

        self.save_state()
        logger.info(f"Task tree initialized. Total topics: {len(self.tasks)}.")

    async def _call_groq_single_key(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        max_tokens: int = 4096,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Call Groq API using exactly ONE rotated key.
        Returns: (success, result_or_error_text, key_label, failure_type)
        """
        managed_key = await self.key_manager.get_next_key()
        key_label = managed_key.label

        headers = {
            "Authorization": f"Bearer {managed_key.api_key}",
            "Content-Type": "application/json",
        }
        body: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        start_time = time.time()
        close_client = False
        if client is None:
            client = httpx.AsyncClient(timeout=60.0)
            close_client = True

        try:
            resp = await client.post(GROQ_CHAT_URL, headers=headers, json=body, timeout=60.0)
            latency_ms = (time.time() - start_time) * 1000

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                await self.key_manager.record_success(managed_key.index, latency_ms)
                return True, content, key_label, None

            elif resp.status_code == 429:
                await self.key_manager.mark_rate_limited(managed_key.index, cooldown_seconds=60.0)
                return False, "429 Rate Limit", key_label, "RATE_LIMIT"

            elif resp.status_code in [401, 403]:
                await self.key_manager.mark_invalid(managed_key.index, reason=f"HTTP {resp.status_code}")
                return False, f"HTTP {resp.status_code} Auth Failure", key_label, "INVALID_KEY"

            else:
                await self.key_manager.record_failure(managed_key.index)
                return False, f"HTTP {resp.status_code}: {resp.text[:100]}", key_label, "SERVER_ERROR"

        except httpx.TimeoutException:
            await self.key_manager.record_failure(managed_key.index)
            return False, "Timeout", key_label, "TIMEOUT"
        except Exception as e:
            await self.key_manager.record_failure(managed_key.index)
            return False, str(e), key_label, "NETWORK_ERROR"
        finally:
            if close_client:
                await client.aclose()

    async def _process_single_topic(self, task: TopicTask, client: httpx.AsyncClient) -> bool:
        """
        Execute the strict sequential pipeline for ONE topic:
        GENERATE NOTE -> VALIDATE -> SAVE -> GENERATE MCQs -> VALIDATE -> DEDUPLICATE -> SAVE -> COMPLETE
        """
        # Resolve Topic model in DB
        async with AsyncSessionLocal() as db:
            sub_res = await db.execute(select(Subject).where(Subject.course_code == task.subject_code))
            subj = sub_res.scalar_one_or_none()
            if not subj:
                logger.error(f"Subject {task.subject_code} not found in DB.")
                task.state = TopicJobState.FAILED
                return False

            u_res = await db.execute(
                select(Unit).where(Unit.subject_id == subj.id, Unit.unit_number == task.unit_number)
            )
            unit = u_res.scalar_one_or_none()
            if not unit:
                logger.error(f"Unit {task.unit_number} not found for {task.subject_code}.")
                task.state = TopicJobState.FAILED
                return False

            t_res = await db.execute(
                select(Topic).where(Topic.unit_id == unit.id, Topic.name.ilike(task.topic_name))
            )
            topic = t_res.scalar_one_or_none()
            if not topic:
                # Create topic if not in DB
                topic = Topic(unit_id=unit.id, name=task.topic_name, sort_order=0)
                db.add(topic)
                await db.commit()
                await db.refresh(topic)

            topic_id = topic.id

            # System user for note authoring
            sys_user = (await db.execute(select(User).order_by(User.id).limit(1))).scalar_one_or_none()
            author_id = sys_user.id if sys_user else 1

        # =========================================================================
        # PHASE 1: NOTE GENERATION & VALIDATION & DB SAVE
        # =========================================================================
        if task.note_status != "SAVED":
            task.state = TopicJobState.GENERATING_NOTE
            note_saved = False

            for attempt in range(1, 4):
                task.note_attempts += 1
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a distinguished university professor authoring a definitive, high-scoring digital "
                            "textbook chapter for computer science undergraduate students. Output strictly a JSON object."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""Generate an in-depth academic study note for:
Subject: {task.subject_code} — {task.subject_name}
Unit: Unit {task.unit_number} ({task.unit_name})
Topic: {task.topic_name}

Your response must be a JSON object with this exact structure:
{{
  "topic": "{task.topic_name}",
  "title": "{task.topic_name}",
  "summary_markdown": "# Comprehensive Academic Theory Note in Markdown with definitions, core principles, syntax code blocks, comparison tables, and university exam traps..."
}}

Requirements:
- 'summary_markdown' must contain extensive, rich Markdown (>400 words).
- Include working code examples (Java/SQL/HTML/JS/Python) where appropriate.
- Include exam traps and edge cases.
- Do NOT include generic AI filler ('as an AI', 'in summary')."""
                    },
                ]

                try:
                    success, raw_result, key_label, fail_type = await self._call_groq_single_key(
                        messages=messages, json_mode=True, max_tokens=4096, client=client
                    )
                    task.note_key = key_label

                    if success:
                        task.state = TopicJobState.VALIDATING_NOTE
                        try:
                            parsed = json.loads(raw_result)
                            markdown = parsed.get("summary_markdown") or parsed.get("content") or ""
                            if not markdown and "sections" in parsed:
                                markdown = f"# {task.topic_name}\n\n" + "\n\n".join(str(s) for s in parsed["sections"])

                            is_valid, reason, cleaned_note = ContentValidator.validate_note(markdown, task.topic_name)
                            if is_valid:
                                # Save Note to Database atomically
                                async with AsyncSessionLocal() as db:
                                    # Delete any placeholder note if needed
                                    existing = (await db.execute(select(Note).where(Note.topic_id == topic_id))).scalar_one_or_none()
                                    if not existing:
                                        db.add(Note(user_id=author_id, topic_id=topic_id, content=cleaned_note))
                                    else:
                                        existing.content = cleaned_note
                                    await db.commit()

                                task.note_status = "SAVED"
                                task.state = TopicJobState.NOTE_COMPLETE
                                note_saved = True
                                logger.info(f"[{task.topic_identifier}] Note SAVED ({key_label}) | Attempt {attempt}")
                                break
                            else:
                                logger.warning(f"[{task.topic_identifier}] Note validation failed: {reason}. Retrying...")
                                task.error_message = reason
                        except Exception as parse_err:
                            logger.warning(f"[{task.topic_identifier}] Note JSON parse error: {parse_err}")
                            task.error_message = str(parse_err)
                    else:
                        logger.warning(f"[{task.topic_identifier}] Note generation failed on {key_label}: {raw_result}")
                        await asyncio.sleep(1.5 * attempt)

                except AllKeysUnavailableError as e:
                    logger.warning(f"[{task.topic_identifier}] All keys rate-limited. Pausing: {e}")
                    await asyncio.sleep(5.0)

            if not note_saved:
                task.state = TopicJobState.RETRY_REQUIRED
                task.error_message = "Note generation failed after 3 attempts"
                self.save_state()
                return False

        # Ensure note is marked complete before proceeding
        task.state = TopicJobState.NOTE_COMPLETE
        self.save_state()

        # =========================================================================
        # PHASE 2: MCQ GENERATION & VALIDATION & DB SAVE
        # =========================================================================
        # Check how many MCQs are needed
        async with AsyncSessionLocal() as db:
            q_cnt_stmt = select(func.count(Question.id)).where(Question.topic_id == topic_id, Question.is_active == True)
            current_mcq_count = (await db.execute(q_cnt_stmt)).scalar() or 0

        task.mcq_count_saved = current_mcq_count
        missing_mcqs = max(0, task.target_mcqs - current_mcq_count)

        if missing_mcqs > 0:
            task.state = TopicJobState.GENERATING_MCQ
            mcq_saved_in_run = 0

            for attempt in range(1, 4):
                if task.mcq_count_saved >= task.target_mcqs:
                    break

                task.mcq_attempts += 1
                batch_to_request = min(10, missing_mcqs + 2)  # Request small buffer

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a university exam controller creating rigorous multiple-choice questions for computer science students. "
                            "Output strictly a JSON object containing an array of questions."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""Generate {batch_to_request} high-quality multiple choice questions for:
Subject: {task.subject_code} — {task.subject_name}
Unit: Unit {task.unit_number} ({task.unit_name})
Topic: {task.topic_name}

Your response must be a JSON object with this exact structure:
{{
  "questions": [
    {{
      "question_text": "Detailed question stem or code prediction challenge...",
      "difficulty": "EASY|MEDIUM|HARD",
      "options": [
        "First option",
        "Second option",
        "Third option",
        "Fourth option"
      ],
      "correct_index": 0,
      "explanation": "Authoritative explanation proving why the correct answer is true based on CS principles."
    }}
  ]
}}

Requirements:
- Exactly 4 options per question.
- 'correct_index' must be an integer from 0 to 3.
- Varied difficulties (mix of Easy, Medium, Hard).
- Include output prediction, debugging, and conceptual questions."""
                    },
                ]

                try:
                    success, raw_result, key_label, fail_type = await self._call_groq_single_key(
                        messages=messages, json_mode=True, max_tokens=2048, client=client
                    )
                    task.mcq_key = key_label

                    if success:
                        task.state = TopicJobState.VALIDATING_MCQ
                        try:
                            parsed = json.loads(raw_result)
                            raw_questions = parsed.get("questions", [])
                            if not isinstance(raw_questions, list):
                                continue

                            valid_mcqs_to_insert = []
                            for q_dict in raw_questions:
                                if task.mcq_count_saved + len(valid_mcqs_to_insert) >= task.target_mcqs:
                                    break

                                is_valid, reason, sanitized_q = ContentValidator.validate_mcq(q_dict, task.topic_name)
                                if not is_valid:
                                    continue

                                # Cross-worker / cross-run duplicate fingerprint check
                                if not self.duplicate_detector.register_if_unique(sanitized_q["question_text"]):
                                    continue

                                valid_mcqs_to_insert.append(sanitized_q)

                            # Save validated unique MCQs to database atomically
                            if valid_mcqs_to_insert:
                                async with AsyncSessionLocal() as db:
                                    for q_data in valid_mcqs_to_insert:
                                        diff_enum = Difficulty[q_data["difficulty"].upper()] if q_data["difficulty"].upper() in Difficulty.__members__ else Difficulty.MEDIUM
                                        new_q = Question(
                                            topic_id=topic_id,
                                            question_text=q_data["question_text"],
                                            question_type=QuestionType.MCQ,
                                            difficulty=diff_enum,
                                            explanation=q_data.get("explanation"),
                                            source_type="GROQ_EXAM_SEEDED",
                                            is_active=True,
                                        )
                                        db.add(new_q)
                                        await db.flush()

                                        for opt in q_data.get("options", []):
                                            db.add(QuestionOption(
                                                question_id=new_q.id,
                                                option_text=opt["option_text"],
                                                is_correct=opt["is_correct"],
                                                sort_order=opt.get("sort_order", 0),
                                            ))
                                    await db.commit()

                                task.mcq_count_saved += len(valid_mcqs_to_insert)
                                missing_mcqs = max(0, task.target_mcqs - task.mcq_count_saved)
                                logger.info(
                                    f"[{task.topic_identifier}] MCQs SAVED (+{len(valid_mcqs_to_insert)}) | Total: {task.mcq_count_saved}/{task.target_mcqs} ({key_label})"
                                )

                        except Exception as parse_err:
                            logger.warning(f"[{task.topic_identifier}] MCQ JSON parse error: {parse_err}")
                    else:
                        logger.warning(f"[{task.topic_identifier}] MCQ generation failed on {key_label}: {raw_result}")
                        await asyncio.sleep(1.5 * attempt)

                except AllKeysUnavailableError as e:
                    logger.warning(f"[{task.topic_identifier}] All keys rate-limited. Pausing: {e}")
                    await asyncio.sleep(5.0)

        # =========================================================================
        # PHASE 3: TOPIC COMPLETION VERIFICATION
        # =========================================================================
        if task.note_status == "SAVED" and task.mcq_count_saved >= task.target_mcqs:
            task.state = TopicJobState.COMPLETE
            task.mcq_status = "SAVED"
            task.error_message = None
            task.last_updated = time.time()
            self.save_state()
            logger.info(f"[{task.topic_identifier}] >>> TOPIC COMPLETE <<<")
            return True
        else:
            task.state = TopicJobState.RETRY_REQUIRED
            task.last_updated = time.time()
            self.save_state()
            return False

    async def run_seeding(
        self,
        subject_filter: Optional[str] = None,
        unit_filter: Optional[int] = None,
        max_topics: Optional[int] = None,
    ) -> None:
        """Run the topic-by-topic seeding pipeline with controlled concurrency."""
        # Find all runnable incomplete tasks
        candidate_tasks = []
        for t in self.tasks.values():
            if t.state != TopicJobState.COMPLETE:
                if subject_filter and t.subject_code != subject_filter.upper():
                    continue
                if unit_filter and t.unit_number != unit_filter:
                    continue
                candidate_tasks.append(t)

        if max_topics:
            candidate_tasks = candidate_tasks[:max_topics]

        total_topics = len(self.tasks)
        completed_initial = sum(1 for t in self.tasks.values() if t.state == TopicJobState.COMPLETE)

        print("\n" + "=" * 65)
        print("SEMESTER OS — TOPIC-BY-TOPIC RESUMABLE CONTENT SEEDING")
        print("=" * 65)
        print(f"Subjects: 5 | Units: 30 | Total Topics: {total_topics}")
        print(f"Initial State: {completed_initial} / {total_topics} topics already COMPLETE")
        print(f"Pending to process: {len(candidate_tasks)} topics")
        print(f"Configured Groq Keys: {self.key_manager.key_count}/5")
        print(f"Worker Concurrency: {self.max_workers}")
        print("=" * 65 + "\n")

        if not candidate_tasks:
            print("All topics are already COMPLETE and verified in the database!")
            return

        queue: asyncio.Queue = asyncio.Queue()
        for t in candidate_tasks:
            await queue.put(t)

        async def worker_loop(w_id: int):
            async with httpx.AsyncClient(timeout=60.0) as client:
                while not queue.empty():
                    try:
                        task: TopicTask = await queue.get()
                    except asyncio.QueueEmpty:
                        break

                    try:
                        success = await self._process_single_topic(task, client)
                        self.save_state()
                    except Exception as e:
                        logger.error(f"Worker {w_id} encountered unhandled error on {task.topic_identifier}: {e}")
                        task.state = TopicJobState.FAILED
                        task.error_message = str(e)
                        self.save_state()
                    finally:
                        queue.task_done()
                        completed_now = sum(1 for t in self.tasks.values() if t.state == TopicJobState.COMPLETE)
                        total_notes = sum(1 for t in self.tasks.values() if t.note_status == "SAVED")
                        total_mcqs = sum(t.mcq_count_saved for t in self.tasks.values())
                        print(
                            f"Progress: [{completed_now}/{total_topics} topics complete ({(completed_now/total_topics)*100:.1f}%)] | "
                            f"Notes: {total_notes}/{total_topics} | MCQs: {total_mcqs} | Duplicates prevented: {self.duplicate_detector.duplicates_prevented_count}"
                        )

        workers = [asyncio.create_task(worker_loop(w_id)) for w_id in range(1, self.max_workers + 1)]
        await asyncio.gather(*workers)

    def print_summary_report(self) -> None:
        """Print final execution summary and key metrics."""
        total = len(self.tasks)
        complete = sum(1 for t in self.tasks.values() if t.state == TopicJobState.COMPLETE)
        notes_saved = sum(1 for t in self.tasks.values() if t.note_status == "SAVED")
        total_mcqs = sum(t.mcq_count_saved for t in self.tasks.values())
        failed = sum(1 for t in self.tasks.values() if t.state in [TopicJobState.FAILED, TopicJobState.RETRY_REQUIRED])

        print("\n" + "=" * 65)
        print("SEMESTER OS — FINAL SEEDING REPORT")
        print("=" * 65)
        print(f"Total Curriculum Topics:    {total}")
        print(f"Completed Topics:           {complete} ({(complete/total)*100:.1f}%)")
        print(f"Official Theory Notes Saved: {notes_saved} / {total}")
        print(f"Validated MCQs Saved:       {total_mcqs}")
        print(f"Duplicates Prevented:       {self.duplicate_detector.duplicates_prevented_count}")
        print(f"Failed / Needs Retry:       {failed}")
        print("\nPer-Key Usage:")
        for k in self.key_manager.get_stats_summary():
            print(f"  {k['label']}: Requests {k['requests']} | Success {k['successes']} | 429s {k['rate_limits']} | Status: {k['status']}")
        
        status_text = "SUCCESS" if complete == total else "PARTIALLY COMPLETE — RESUMABLE"
        print(f"\nFinal Seed Status: {status_text}")
        print("=" * 65 + "\n")
