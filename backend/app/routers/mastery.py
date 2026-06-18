"""Mastery scores."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Mastery, User
from ..schemas import MasteryOut

router = APIRouter(prefix="/mastery", tags=["mastery"])


@router.get("", response_model=list[MasteryOut])
def list_mastery(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Mastery)
        .filter(Mastery.user_id == user.id)
        .order_by(Mastery.mastery_score.desc())
        .all()
    )
    return [MasteryOut.model_validate(m) for m in rows]
