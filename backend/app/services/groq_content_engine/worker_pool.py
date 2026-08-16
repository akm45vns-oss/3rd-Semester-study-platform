"""
Asynchronous Multi-Worker Pool for Concurrent Groq LLM Content Generation.

Features:
- Key-aware isolated execution (Exactly 1 key per HTTP request)
- Structured JSON output mode (response_format: {"type": "json_object"})
- Exponential backoff & key failover on 429/5xx errors
- Strict application-side validation before job approval
- Cross-worker duplicate collision prevention
"""
import json
import time
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional, List, Tuple
from app.core.config import settings
from app.services.groq_content_engine.key_manager import GroqKeyManager, AllKeysUnavailableError, KeyStatus
from app.services.groq_content_engine.validators import ContentValidator, DuplicateDetector
from app.services.groq_content_engine.job_queue import GenerationJob, JobStatus, ContentType, ContentJobQueue

logger = logging.getLogger("GroqWorkerPool")

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqWorkerPool:
    """
    Spawns and orchestrates up to 5 concurrent asynchronous workers to consume the ContentJobQueue.
    """

    def __init__(
        self,
        key_manager: GroqKeyManager,
        job_queue: ContentJobQueue,
        duplicate_detector: DuplicateDetector,
        model_name: Optional[str] = None,
        max_concurrency: int = 5,
    ):
        self.key_manager = key_manager
        self.job_queue = job_queue
        self.duplicate_detector = duplicate_detector
        self.model_name = model_name or getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_concurrency = min(max_concurrency, max(1, key_manager.key_count))

    async def execute_job(self, job: GenerationJob, client: httpx.AsyncClient) -> bool:
        """
        Execute a single generation job with key rotation and exponential backoff.
        Returns True if approved and validated, False otherwise.
        """
        self.job_queue.update_job_status(job.job_id, JobStatus.GENERATING)
        start_time = time.time()

        for attempt in range(1, job.max_attempts + 1):
            try:
                # 1. Acquire an available healthy key from the manager
                managed_key = await self.key_manager.get_next_key()
                job.assigned_key = managed_key.label

                # 2. Build prompt payload based on content type
                messages, response_format = self._build_prompt_payload(job)

                # 3. Perform HTTP request to Groq API (Single key isolation)
                req_start = time.time()
                headers = {
                    "Authorization": f"Bearer {managed_key.api_key}",
                    "Content-Type": "application/json",
                }
                body = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.3,
                    "response_format": response_format,
                    "max_tokens": 4096 if job.content_type == ContentType.NOTE else 2048,
                }

                response = await client.post(GROQ_CHAT_URL, headers=headers, json=body, timeout=60.0)
                latency_ms = (time.time() - req_start) * 1000

                # 4. Handle HTTP Status Codes
                if response.status_code == 200:
                    resp_data = response.json()
                    raw_content = resp_data["choices"][0]["message"]["content"]
                    await self.key_manager.record_success(managed_key.index, latency_ms)

                    # 5. Application-side Validation
                    is_valid, reason, validated_payload = self._validate_response(job, raw_content)
                    if is_valid:
                        self.job_queue.update_job_status(
                            job.job_id,
                            JobStatus.APPROVED,
                            assigned_key=managed_key.label,
                            payload=validated_payload,
                        )
                        logger.info(
                            f"[{job.job_id}] APPROVED | {managed_key.label} | {latency_ms/1000:.2f}s | Attempt {attempt}"
                        )
                        return True
                    else:
                        logger.warning(f"[{job.job_id}] REJECTED validation ({reason}) on {managed_key.label}. Retrying...")
                        job.error_message = reason

                elif response.status_code == 429:
                    # Rate limit encountered
                    await self.key_manager.mark_rate_limited(managed_key.index, cooldown_seconds=60.0)
                    logger.warning(f"[{job.job_id}] 429 Rate Limit on {managed_key.label}. Switching keys...")
                    await asyncio.sleep(1.5 * attempt)

                elif response.status_code in [401, 403]:
                    # Auth failure
                    await self.key_manager.mark_invalid(managed_key.index, reason=f"HTTP {response.status_code}")
                    logger.error(f"[{job.job_id}] Invalid key on {managed_key.label}. Switching keys...")

                else:
                    # 5xx or other transient server errors
                    await self.key_manager.record_failure(managed_key.index)
                    logger.warning(f"[{job.job_id}] HTTP {response.status_code} on {managed_key.label}. Retrying...")
                    await asyncio.sleep(2.0 * attempt)

            except AllKeysUnavailableError as e:
                logger.warning(f"[{job.job_id}] Pausing: {e}")
                await asyncio.sleep(5.0)

            except httpx.TimeoutException:
                logger.warning(f"[{job.job_id}] Request timeout. Retrying with next key...")
                await asyncio.sleep(2.0)

            except Exception as e:
                logger.error(f"[{job.job_id}] Unexpected worker error: {e}")
                await asyncio.sleep(2.0)

        # Max attempts exceeded
        self.job_queue.update_job_status(
            job.job_id,
            JobStatus.FAILED,
            error_message=job.error_message or "Max retry attempts exceeded",
        )
        logger.error(f"[{job.job_id}] FAILED after {job.max_attempts} attempts.")
        return False

    def _build_prompt_payload(self, job: GenerationJob) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
        """Construct structured output prompt messages for Groq LLM."""
        if job.content_type == ContentType.NOTE:
            system_prompt = (
                "You are an expert university professor creating an authoritative, comprehensive digital textbook note "
                "for computer science undergraduate students. You must output strictly a JSON object conforming to the schema."
            )
            user_prompt = f"""Generate an in-depth academic study note for:
Subject: {job.subject_code}
Unit: Unit {job.unit_number} ({job.unit_name})
Topic: {job.topic_name}

Your response must be a JSON object with this exact structure:
{{
  "topic": "{job.topic_name}",
  "title": "{job.topic_name}",
  "summary_markdown": "# Comprehensive Academic Theory Note in Markdown with formal definitions, key bullet points, syntax blocks, comparative tables, and university exam tips..."
}}

Requirements:
- 'summary_markdown' must be comprehensive (>500 words of rich markdown).
- Include working code examples (Java/SQL/JS/Python) where appropriate.
- Include exam traps and edge cases.
- Do NOT include generic AI filler ('as an AI', 'in summary')."""
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ], {"type": "json_object"}

        else:  # MCQ Batch
            system_prompt = (
                "You are a university exam controller creating rigorous multiple-choice questions for computer science students. "
                "Output strictly a JSON object containing an array of questions."
            )
            user_prompt = f"""Generate {job.question_count} high-quality, non-trivial multiple choice questions for:
Subject: {job.subject_code}
Unit: Unit {job.unit_number} ({job.unit_name})
Topic: {job.topic_name} (Batch #{job.batch_index})

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
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ], {"type": "json_object"}

    def _validate_response(self, job: GenerationJob, raw_content: str) -> Tuple[bool, str, Any]:
        """Validate JSON output against strict schema and duplicate rules."""
        try:
            parsed = json.loads(raw_content)
        except Exception as e:
            return False, f"Invalid JSON syntax from LLM: {e}", None

        if job.content_type == ContentType.NOTE:
            markdown = parsed.get("summary_markdown") or parsed.get("content") or ""
            if not markdown and "sections" in parsed:
                markdown = f"# {job.topic_name}\n\n" + "\n\n".join(str(s) for s in parsed["sections"])

            is_valid, reason, cleaned_note = ContentValidator.validate_note(markdown, job.topic_name)
            if not is_valid:
                return False, reason, None
            return True, "Valid", cleaned_note

        else:  # MCQ
            raw_questions = parsed.get("questions")
            if not isinstance(raw_questions, list) or len(raw_questions) == 0:
                return False, "Missing 'questions' array in JSON payload", None

            approved_mcqs = []
            for q in raw_questions:
                is_valid, reason, sanitized_mcq = ContentValidator.validate_mcq(q, job.topic_name)
                if not is_valid:
                    logger.debug(f"Rejected individual MCQ: {reason}")
                    continue

                # Cross-Worker Duplicate Check
                if not self.duplicate_detector.register_if_unique(sanitized_mcq["question_text"]):
                    logger.warning(f"Cross-Worker Duplicate Prevented: {sanitized_mcq['question_text'][:60]}...")
                    continue

                approved_mcqs.append(sanitized_mcq)

            if len(approved_mcqs) == 0:
                return False, "Zero valid, non-duplicate questions in batch", None

            return True, "Valid", approved_mcqs

    async def run_worker_pool(
        self,
        pending_jobs: List[GenerationJob],
        progress_callback: Optional[Any] = None,
    ) -> None:
        """Process pending jobs with a controlled asynchronous worker pool."""
        queue: asyncio.Queue = asyncio.Queue()
        for j in pending_jobs:
            await queue.put(j)

        async def worker(worker_id: int):
            async with httpx.AsyncClient() as client:
                while not queue.empty():
                    try:
                        job: GenerationJob = await queue.get()
                    except asyncio.QueueEmpty:
                        break

                    success = await self.execute_job(job, client)
                    queue.task_done()
                    self.job_queue.save_checkpoint()

                    if progress_callback:
                        progress_callback(job, success)

        workers = [asyncio.create_task(worker(w_id)) for w_id in range(1, self.max_concurrency + 1)]
        await asyncio.gather(*workers)
