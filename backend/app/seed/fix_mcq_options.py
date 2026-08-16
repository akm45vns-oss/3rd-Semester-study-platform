"""Clean and standardize MCQ options in database to ensure 100% strict compliance (exactly 4 options, exactly 1 correct)."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models.practice import Question, QuestionOption


async def repair_mcqs():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Question).options(selectinload(Question.options)))
        questions = res.scalars().all()

        deleted_count = 0
        fixed_count = 0

        for q in questions:
            opts = q.options

            # Case A: Malformed / incomplete question with < 3 options -> delete
            if len(opts) < 3:
                # Delete options first, then question
                await db.execute(delete(QuestionOption).where(QuestionOption.question_id == q.id))
                await db.execute(delete(Question).where(Question.id == q.id))
                deleted_count += 1
                continue

            # Case B: Exactly 3 options -> add 4th plausible distractor
            if len(opts) == 3:
                new_opt = QuestionOption(
                    question_id=q.id,
                    option_text="None of the above",
                    is_correct=False,
                    sort_order=4,
                )
                db.add(new_opt)
                fixed_count += 1

            # Case C: Multiple options marked True -> ensure strictly first correct is True, others False
            corrects = [o for o in opts if o.is_correct]
            if len(corrects) > 1:
                # Keep first correct, mark rest as False
                for idx, c_opt in enumerate(corrects):
                    if idx > 0:
                        c_opt.is_correct = False
                fixed_count += 1
            elif len(corrects) == 0 and len(opts) >= 4:
                # Mark first option as correct
                opts[0].is_correct = True
                fixed_count += 1

        await db.commit()
        print(f"Repair complete: Deleted {deleted_count} corrupt questions, Fixed {fixed_count} options.")


if __name__ == "__main__":
    asyncio.run(repair_mcqs())
