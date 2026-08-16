"""
Automated Groq-Powered Question Seeding, Quality Validation & Checkpoint Pipeline.
Supports CLI arguments:
  --mode [mcq | descriptive | all]
  --subject [CAP392 | CAP206 | CAP135 | CAB213 | CAB114]
  --unit [1-6]
  --topic <topic_id>
  --count <number>
  --dry-run
"""
import asyncio
import argparse
import logging
import json
import re
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal, create_tables
from app.models.curriculum import Subject, Unit, Topic
from app.models.practice import Question, QuestionOption, QuestionType, Difficulty, DescriptiveQuestion
from app.seed.descriptive_data import DESCRIPTIVE_QUESTIONS_DATA

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ExamSeeder")


# ── Strict Pydantic Schemas for AI Validation ──

class AIMCQOption(BaseModel):
    label: str  # A, B, C, D
    text: str = Field(min_length=1)


class AIMCQItem(BaseModel):
    question: str = Field(min_length=10)
    options: List[AIMCQOption] = Field(min_length=4, max_length=4)
    correct_option: str  # A, B, C, or D
    explanation: str = Field(min_length=10)
    difficulty: str = "MEDIUM"


class AIDescriptiveItem(BaseModel):
    question: str = Field(min_length=15)
    marks: int = 10
    difficulty: str = "MEDIUM"
    question_type: str = "THEORY_EXPLANATION"
    answer_outline: List[str] = Field(min_length=3)
    model_answer: str = Field(min_length=100)
    key_points: List[str] = Field(min_length=2)
    exam_tips: List[str] = Field(min_length=1)
    important_terms: List[str] = Field(default_factory=list)


# ── AI Generation with Multi-Key & Multi-Model Rotation ──

class AIQuestionGenerator:
    def __init__(self):
        self.api_keys = settings.get_groq_keys()
        self.key_index = 0
        self.models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        self.model_index = 0

    def get_current_key(self) -> Optional[str]:
        if not self.api_keys:
            return None
        return self.api_keys[self.key_index % len(self.api_keys)]

    def rotate_key(self):
        if self.api_keys:
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            logger.info(f"[INFO] Rotated API Key (Index: {self.key_index})")

    def rotate_model(self):
        self.model_index = (self.model_index + 1) % len(self.models)
        logger.info(f"[INFO] Switched Fallback Model to: {self.models[self.model_index]}")

    async def _call_groq(self, system_prompt: str, user_prompt: str, max_retries: int = 4) -> Optional[str]:
        for attempt in range(max_retries):
            key = self.get_current_key()
            model = self.models[self.model_index]
            if not key:
                logger.warning("[WARN] No Groq API Key configured. Skipping live AI generation.")
                return None

            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            }

            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    elif resp.status_code == 429:
                        logger.warning(f"[INFO] Rate Limit 429 (Key Index: {self.key_index}, Model: {model}). Rotating key...")
                        self.rotate_key()
                        await asyncio.sleep(1.0)
                    else:
                        logger.warning(f"[INFO] Groq API returned {resp.status_code}. Fallback...")
                        self.rotate_model()
            except Exception as e:
                logger.warning(f"[INFO] Connection error on attempt {attempt+1}: {type(e).__name__}")
                self.rotate_key()
                await asyncio.sleep(1.0)

        return None

    async def generate_mcqs(self, subject: str, unit: int, topic: str, count: int = 3) -> List[AIMCQItem]:
        system_prompt = (
            "You are an expert university computer science examiner creating official midterm/end-term MCQs.\n"
            "Return STRICT JSON with key 'questions' containing a list of questions.\n"
            "Each question MUST have: 'question', 'options' (list of 4 with 'label': 'A'|'B'|'C'|'D' and 'text'), "
            "'correct_option' ('A'|'B'|'C'|'D'), 'explanation', 'difficulty' ('EASY'|'MEDIUM'|'HARD').\n"
            "Rules: Exactly 4 options, 1 correct, clear explanations, syllabus-bound."
        )
        user_prompt = (
            f"Subject: {subject}\nUnit: {unit}\nTopic: {topic}\n"
            f"Generate exactly {count} high-quality, non-trivial examination MCQs for this topic."
        )
        raw = await self._call_groq(system_prompt, user_prompt)
        if not raw:
            return []

        try:
            parsed = json.loads(raw)
            items = parsed.get("questions", [])
            valid_list = []
            for it in items:
                try:
                    obj = AIMCQItem(**it)
                    valid_list.append(obj)
                except Exception:
                    continue
            return valid_list
        except Exception:
            return []

    async def generate_descriptive(self, subject: str, unit: int, topic: str) -> Optional[AIDescriptiveItem]:
        system_prompt = (
            "You are a university professor creating an official 10-Mark Descriptive Examination Question.\n"
            "Return STRICT JSON with keys: 'question', 'marks' (10), 'difficulty' ('MEDIUM'|'HARD'), "
            "'question_type' ('THEORY_EXPLANATION'|'ARCHITECTURE_DERIVATION'|'CODE_IMPLEMENTATION'), "
            "'answer_outline' (list of 4-5 outline steps), 'model_answer' (comprehensive markdown answer of 250+ words), "
            "'key_points' (list of 4 marking criteria), 'exam_tips' (list of 2 student tips), 'important_terms' (list of keywords)."
        )
        user_prompt = (
            f"Subject: {subject}\nUnit: {unit}\nTopic: {topic}\n"
            f"Create an authoritative 10-Mark university examination question with model answer and marking scheme."
        )
        raw = await self._call_groq(system_prompt, user_prompt)
        if not raw:
            return None

        try:
            parsed = json.loads(raw)
            if "question" in parsed:
                return AIDescriptiveItem(**parsed)
            elif "questions" in parsed and len(parsed["questions"]) > 0:
                return AIDescriptiveItem(**parsed["questions"][0])
        except Exception:
            pass
        return None


# ── Idempotent Seeding Pipeline ──

async def seed_static_descriptive_questions(db: AsyncSession, dry_run: bool = False) -> int:
    """Seed authoritative pre-verified 10-mark descriptive questions."""
    inserted = 0
    for data in DESCRIPTIVE_QUESTIONS_DATA:
        # Find topic
        stmt = (
            select(Topic)
            .join(Unit, Topic.unit_id == Unit.id)
            .join(Subject, Unit.subject_id == Subject.id)
            .where(
                Subject.course_code == data["course_code"],
                Unit.unit_number == data["unit_number"],
                Topic.name.ilike(f"%{data['topic_keyword']}%")
            )
        )
        res = await db.execute(stmt)
        topic = res.scalars().first()
        if not topic:
            # Fallback to first topic of the unit
            unit_stmt = (
                select(Topic)
                .join(Unit, Topic.unit_id == Unit.id)
                .join(Subject, Unit.subject_id == Subject.id)
                .where(
                    Subject.course_code == data["course_code"],
                    Unit.unit_number == data["unit_number"]
                )
            )
            ures = await db.execute(unit_stmt)
            topic = ures.scalars().first()

        if not topic:
            continue

        # Check existing
        existing_res = await db.execute(
            select(DescriptiveQuestion).where(
                DescriptiveQuestion.topic_id == topic.id,
                DescriptiveQuestion.question_text == data["question_text"]
            )
        )
        if existing_res.scalar_one_or_none():
            continue

        # Find subject & unit
        ures = await db.execute(select(Unit).where(Unit.id == topic.unit_id))
        unit = ures.scalar_one()

        if not dry_run:
            dq = DescriptiveQuestion(
                subject_id=unit.subject_id,
                unit_id=unit.id,
                topic_id=topic.id,
                question_text=data["question_text"],
                marks=data["marks"],
                difficulty=Difficulty(data["difficulty"]),
                question_type=data["question_type"],
                answer_outline=data["answer_outline"],
                model_answer=data["model_answer"],
                key_points=data["key_points"],
                exam_tips=data["exam_tips"],
                important_terms=data["important_terms"],
            )
            db.add(dq)
            inserted += 1

    if not dry_run:
        await db.commit()

    return inserted


async def run_exam_seeder(
    mode: str = "all",
    subject_code: Optional[str] = None,
    unit_number: Optional[int] = None,
    topic_id: Optional[int] = None,
    count_per_topic: int = 2,
    dry_run: bool = False,
):
    """Main exam question seeder execution engine."""
    await create_tables()
    generator = AIQuestionGenerator()

    async with AsyncSessionLocal() as db:
        logger.info(f"=== Starting Semester OS Exam Question Seeder ===")
        logger.info(f"Mode: {mode} | Dry Run: {dry_run} | Target Subject: {subject_code or 'ALL'}")

        # 1. First seed pre-curated static 10-mark descriptive questions
        static_count = await seed_static_descriptive_questions(db, dry_run=dry_run)
        logger.info(f"[INFO] Verified Static 10-Mark Questions Inserted: {static_count}")

        # 2. Select topics to process
        stmt = (
            select(Topic)
            .options(selectinload(Topic.unit).selectinload(Unit.subject))
            .join(Unit, Topic.unit_id == Unit.id)
            .join(Subject, Unit.subject_id == Subject.id)
        )
        if topic_id:
            stmt = stmt.where(Topic.id == topic_id)
        if subject_code:
            stmt = stmt.where(Subject.course_code == subject_code)
        if unit_number:
            stmt = stmt.where(Unit.unit_number == unit_number)

        res = await db.execute(stmt)
        topics = res.scalars().all()
        logger.info(f"[INFO] Found {len(topics)} syllabus topics matching criteria.")

        total_mcqs_inserted = 0
        total_desc_inserted = 0
        total_duplicates_skipped = 0

        for idx, topic in enumerate(topics, 1):
            sub = topic.unit.subject
            u = topic.unit
            logger.info(f"\n[{idx}/{len(topics)}] Topic: {topic.name} ({sub.course_code} · Unit {u.unit_number})")

            # Check existing MCQs count for this topic
            q_cnt_res = await db.execute(
                select(func.count(Question.id)).where(Question.topic_id == topic.id)
            )
            existing_mcq_count = q_cnt_res.scalar() or 0

            # ── A. MCQ Seeding ──
            if mode in ["mcq", "all"] and existing_mcq_count < 4:
                logger.info(f"  Fetching MCQs from Groq (Target: {count_per_topic})...")
                generated_mcqs = await generator.generate_mcqs(sub.name, u.unit_number, topic.name, count=count_per_topic)
                
                valid_count = 0
                for gq in generated_mcqs:
                    # Duplicate check
                    dup_res = await db.execute(
                        select(Question).where(
                            Question.topic_id == topic.id,
                            Question.question_text == gq.question
                        )
                    )
                    if dup_res.scalar_one_or_none():
                        total_duplicates_skipped += 1
                        continue

                    if not dry_run:
                        # Insert Question
                        q_obj = Question(
                            topic_id=topic.id,
                            question_text=gq.question,
                            question_type=QuestionType.MCQ,
                            difficulty=Difficulty(gq.difficulty.upper() if gq.difficulty.upper() in ["EASY", "MEDIUM", "HARD"] else "MEDIUM"),
                            explanation=gq.explanation,
                            source_type="GROQ_EXAM_SEEDED",
                        )
                        db.add(q_obj)
                        await db.flush()

                        # Insert Options
                        for opt in gq.options:
                            is_corr = opt.label.strip().upper() == gq.correct_option.strip().upper()
                            db.add(
                                QuestionOption(
                                    question_id=q_obj.id,
                                    option_text=opt.text,
                                    is_correct=is_corr,
                                    sort_order=ord(opt.label.upper()) - ord('A') if len(opt.label) == 1 else 0,
                                )
                            )
                        valid_count += 1
                        total_mcqs_inserted += 1
                    else:
                        valid_count += 1

                logger.info(f"  Valid MCQs: {valid_count} | Duplicates: {total_duplicates_skipped}")

            # ── B. Descriptive 10-Mark Seeding ──
            if mode in ["descriptive", "all"] and idx % 3 == 0:  # Seed 1 descriptive every 3 topics
                # Check existing descriptive
                d_cnt_res = await db.execute(
                    select(func.count(DescriptiveQuestion.id)).where(DescriptiveQuestion.topic_id == topic.id)
                )
                if (d_cnt_res.scalar() or 0) == 0:
                    logger.info("  Generating 10-Mark Descriptive Question...")
                    desc_item = await generator.generate_descriptive(sub.name, u.unit_number, topic.name)
                    if desc_item:
                        if not dry_run:
                            dq = DescriptiveQuestion(
                                subject_id=sub.id,
                                unit_id=u.id,
                                topic_id=topic.id,
                                question_text=desc_item.question,
                                marks=10,
                                difficulty=Difficulty(desc_item.difficulty.upper() if desc_item.difficulty.upper() in ["EASY", "MEDIUM", "HARD"] else "MEDIUM"),
                                question_type=desc_item.question_type,
                                answer_outline=desc_item.answer_outline,
                                model_answer=desc_item.model_answer,
                                key_points=desc_item.key_points,
                                exam_tips=desc_item.exam_tips,
                                important_terms=desc_item.important_terms,
                            )
                            db.add(dq)
                            total_desc_inserted += 1
                        logger.info("  10-Mark Question Validated and Ready.")

            if not dry_run:
                await db.commit()

        logger.info("\n=== Seeding Summary ===")
        logger.info(f"MCQs Inserted: {total_mcqs_inserted}")
        logger.info(f"10-Mark Questions Inserted: {total_desc_inserted + static_count}")
        logger.info(f"Duplicates Skipped: {total_duplicates_skipped}")
        if dry_run:
            logger.info("DRY RUN COMPLETE — No database modifications made.")


def main():
    parser = argparse.ArgumentParser(description="Semester OS Exam Seeder")
    parser.add_argument("--mode", choices=["mcq", "descriptive", "all"], default="all")
    parser.add_argument("--subject", type=str, default=None)
    parser.add_argument("--unit", type=int, default=None)
    parser.add_argument("--topic", type=int, default=None)
    parser.add_argument("--count", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    asyncio.run(
        run_exam_seeder(
            mode=args.mode,
            subject_code=args.subject,
            unit_number=args.unit,
            topic_id=args.topic,
            count_per_topic=args.count,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
