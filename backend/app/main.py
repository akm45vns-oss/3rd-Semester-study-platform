"""
Semester OS — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables
import app.models  # noqa: F401
from app.routers import auth, curriculum, progress, practice, coding, intelligence, ai_study, exams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("semester_os")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and initialize SQLite WAL mode on startup."""
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Personal Semester Study OS — structured learning, practice, assessments, and progress tracking.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Safely log unhandled errors and return sanitized JSON responses."""
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please retry your request."},
    )


# Register routers
app.include_router(auth.router)
app.include_router(curriculum.router)
app.include_router(progress.router)
app.include_router(practice.router)
app.include_router(coding.router)
app.include_router(intelligence.router)
app.include_router(ai_study.router)
app.include_router(exams.router)


@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/ready")
async def readiness():
    """Readiness probe checking database connectivity."""
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal
    import shutil

    db_ok = False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        logger.error(f"Readiness check database error: {e}")
        db_ok = False

    runtimes = {
        "python": shutil.which("python") is not None or shutil.which("python3") is not None,
        "java": shutil.which("java") is not None,
        "node": shutil.which("node") is not None,
    }

    is_ready = db_ok

    return {
        "ready": is_ready,
        "database": "connected" if db_ok else "disconnected",
        "runtimes": runtimes,
        "version": settings.APP_VERSION,
    }
