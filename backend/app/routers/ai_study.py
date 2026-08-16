"""
AI Study Assistant & Dynamic Content Generation Router.
Powered by Groq API (Llama 3.3 70B).
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.curriculum import Topic, Unit, Subject
from app.models.progress import Note
from app.models.practice import Question, QuestionOption, CodingProblem, QuestionType, Difficulty
from app.services.ai_generator import GroqAIGenerator
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
async def get_ai_status(_: User = Depends(get_current_user)):
    """Check if AI generation is configured and available."""
    ai = GroqAIGenerator()
    return {
        "is_configured": ai.is_configured(),
        "provider": "Groq",
        "model": ai.model,
    }


@router.post("/configure-key")
async def configure_groq_key(
    api_key: str = Body(..., embed=True),
    _: User = Depends(get_current_user),
):
    """Dynamically set or update the Groq API key for the current session."""
    key = api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")
    settings.GROQ_API_KEY = key
    return {"success": True, "message": "Groq API key configured successfully"}


@router.post("/generate-notes/{topic_id}")
async def generate_topic_notes(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate comprehensive academic notes for a topic using AI and save to user's notes."""
    stmt = (
        select(Topic)
        .options(selectinload(Topic.unit).selectinload(Unit.subject))
        .where(Topic.id == topic_id)
    )
    res = await db.execute(stmt)
    topic = res.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    ai = GroqAIGenerator()
    if not ai.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Groq API key not configured. Please set GROQ_API_KEY in backend/.env or configure it in settings.",
        )

    try:
        notes_md = await ai.generate_academic_notes(
            course_code=topic.unit.subject.course_code,
            subject_name=topic.unit.subject.name,
            unit_number=topic.unit.unit_number,
            unit_name=topic.unit.name,
            topic_name=topic.name,
        )

        note = Note(
            user_id=current_user.id,
            topic_id=topic.id,
            content=notes_md,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)

        return {
            "success": True,
            "note_id": note.id,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-quiz/{topic_id}")
async def generate_topic_quiz(
    topic_id: int,
    count: int = Body(3, embed=True),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Generate custom practice questions for a topic on the fly."""
    stmt = (
        select(Topic)
        .options(selectinload(Topic.unit).selectinload(Unit.subject))
        .where(Topic.id == topic_id)
    )
    res = await db.execute(stmt)
    topic = res.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    ai = GroqAIGenerator()
    if not ai.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Groq API key not configured. Please set GROQ_API_KEY in backend/.env",
        )

    try:
        questions_data = await ai.generate_topic_questions(
            course_code=topic.unit.subject.course_code,
            subject_name=topic.unit.subject.name,
            unit_number=topic.unit.unit_number,
            unit_name=topic.unit.name,
            topic_name=topic.name,
            count=min(max(count, 1), 10),
        )

        saved_questions = []
        for q_item in questions_data:
            q_type_str = q_item.get("question_type", "MCQ")
            q_type = QuestionType.MCQ
            if q_type_str in QuestionType.__members__:
                q_type = QuestionType[q_type_str]

            diff_str = q_item.get("difficulty", "MEDIUM").upper()
            diff = Difficulty.MEDIUM
            if diff_str in Difficulty.__members__:
                diff = Difficulty[diff_str]

            q_obj = Question(
                topic_id=topic.id,
                question_text=q_item.get("question_text", ""),
                question_type=q_type,
                difficulty=diff,
                explanation=q_item.get("explanation", ""),
                source_type="ADDITIONAL_LEARNING",
            )
            db.add(q_obj)
            await db.flush()

            for opt_idx, opt in enumerate(q_item.get("options", [])):
                opt_obj = QuestionOption(
                    question_id=q_obj.id,
                    option_text=opt.get("text", ""),
                    is_correct=opt.get("is_correct", False),
                    sort_order=opt_idx,
                )
                db.add(opt_obj)

            saved_questions.append(q_obj.id)

        await db.commit()
        return {
            "success": True,
            "created_count": len(saved_questions),
            "question_ids": saved_questions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
