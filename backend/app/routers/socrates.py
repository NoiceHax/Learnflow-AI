"""Ask Socrates: guided, Socratic AI tutoring with session history."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import ChatMessage, User
from ..schemas import ChatRequest, ChatResponse, ChatTurn
from ..services.llm import ask_socrates
from ..services.rate_limiter import limiter

router = APIRouter(prefix="/socrates", tags=["socrates"])


def _rate_limit_headers(user_id: str) -> dict[str, str]:
    """Build X-RateLimit-* headers for the Socrates chat endpoint."""
    info = limiter.get_remaining(
        user_id=user_id,
        action="socrates",
        limit_per_minute=settings.rate_limit_socrates_minute,
        limit_per_day=settings.rate_limit_socrates_daily,
    )
    headers = {
        "X-RateLimit-Limit": f"{settings.rate_limit_socrates_minute}/min, {settings.rate_limit_socrates_daily}/day",
        "X-RateLimit-Remaining": str(min(info["remaining_minute"], info["remaining_daily"])),
    }
    if info["retry_after"] > 0:
        headers["Retry-After"] = str(info["retry_after"])
    return headers


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if limiter.is_rate_limited(
        user_id=user.id,
        action="socrates",
        limit_per_minute=settings.rate_limit_socrates_minute,
        limit_per_day=settings.rate_limit_socrates_daily,
    ):
        headers = _rate_limit_headers(user.id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests to Socrates tutoring chat. Please wait a bit or try again tomorrow.",
            headers=headers,
        )

    session_id = body.session_id or uuid.uuid4().hex

    prior = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
        .all()
    )
    history: list[dict[str, str]] = []
    for m in prior:
        history.append({"role": "user", "content": m.message})
        history.append({"role": "socrates", "content": m.response})

    context = body.context.model_dump() if body.context else None
    chapter_label = (context or {}).get("chapter") or body.chapter_context
    reply, powered_by, difficulty = ask_socrates(body.message, history, body.chapter_context, context, db=db)

    db.add(
        ChatMessage(
            user_id=user.id,
            session_id=session_id,
            message=body.message,
            response=reply,
            chapter_context=chapter_label,
            difficulty_level=difficulty,
        )
    )
    db.commit()

    response_data = ChatResponse(session_id=session_id, reply=reply, powered_by=powered_by, difficulty=difficulty)
    headers = _rate_limit_headers(user.id)
    return JSONResponse(
        content=response_data.model_dump(),
        headers=headers,
    )


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(
            ChatMessage.session_id,
            func.min(ChatMessage.message).label("first_message"),
            func.max(ChatMessage.timestamp).label("last_at"),
            func.count(ChatMessage.id).label("turns"),
        )
        .filter(ChatMessage.user_id == user.id)
        .group_by(ChatMessage.session_id)
        .order_by(func.max(ChatMessage.timestamp).desc())
        .all()
    )
    return [
        {
            "session_id": r.session_id,
            "preview": (r.first_message or "")[:80],
            "last_at": r.last_at,
            "turns": r.turns,
        }
        for r in rows
    ]


@router.get("/sessions/{session_id}", response_model=list[ChatTurn])
def get_session(
    session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
        .all()
    )
    turns: list[ChatTurn] = []
    for m in msgs:
        turns.append(ChatTurn(id=m.id + "-u", role="user", content=m.message, timestamp=m.timestamp))
        turns.append(ChatTurn(id=m.id + "-s", role="socrates", content=m.response, timestamp=m.timestamp, difficulty=m.difficulty_level))
    return turns
