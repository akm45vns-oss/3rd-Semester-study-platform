"""Authentication router: register, login, get current user, with abuse throttling."""
import time
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory failed login tracking: key -> list of timestamp floats
_FAILED_ATTEMPTS: dict[str, list[float]] = defaultdict(list)
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_WINDOW_SECONDS = 60


def _check_rate_limit(key: str):
    """Check if key has exceeded failed attempts in the lockout window."""
    now = time.time()
    # Prune timestamps older than window
    _FAILED_ATTEMPTS[key] = [t for t in _FAILED_ATTEMPTS[key] if now - t < _LOCKOUT_WINDOW_SECONDS]
    if len(_FAILED_ATTEMPTS[key]) >= _MAX_FAILED_ATTEMPTS:
        retry_after = int(_LOCKOUT_WINDOW_SECONDS - (now - _FAILED_ATTEMPTS[key][0]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please wait {max(1, retry_after)} seconds before retrying.",
            headers={"Retry-After": str(max(1, retry_after))},
        )


def _record_failed_attempt(key: str):
    """Record a failed login attempt."""
    _FAILED_ATTEMPTS[key].append(time.time())


def _clear_failed_attempts(key: str):
    """Clear failed attempts on successful login."""
    if key in _FAILED_ATTEMPTS:
        del _FAILED_ATTEMPTS[key]


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check email uniqueness
    existing_email = await db.execute(select(User).where(User.email == data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{data.username}"

    # Check rate limit before verifying
    _check_rate_limit(rate_key)

    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        _record_failed_attempt(rate_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    # Clear rate limit counter on success
    _clear_failed_attempts(rate_key)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
