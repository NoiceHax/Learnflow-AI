"""Personalised learning path."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Chapter, LearningPathItem, Mastery, Subject, User
from ..schemas import LearningPathOut, PathItem
from ..services import learning_path as lp

router = APIRouter(prefix="/learning-path", tags=["learning-path"])


def _build(db: Session, user_id: str) -> LearningPathOut:
    items = (
        db.query(LearningPathItem)
        .filter(LearningPathItem.user_id == user_id)
        .order_by(LearningPathItem.position)
        .all()
    )
    chapters = {c.id: c for c in db.query(Chapter).all()}
    subjects = {s.id: s for s in db.query(Subject).all()}
    mastery = {
        m.chapter_id: m.mastery_score
        for m in db.query(Mastery).filter(Mastery.user_id == user_id).all()
    }

    out: list[PathItem] = []
    current = next_ = None
    for it in items:
        ch = chapters.get(it.chapter_id)
        if ch is None:
            continue
        subj = subjects.get(ch.subject_id)
        out.append(
            PathItem(
                chapter_id=ch.id,
                chapter_name=ch.chapter_name,
                slug=ch.slug,
                subject=subj.name if subj else "",
                position=it.position,
                status=it.status,
                is_weak=it.is_weak,
                reason=it.reason,
                mastery=round(mastery.get(ch.id, 0.0), 1),
                jee_weightage=ch.jee_weightage,
            )
        )
        if it.status == "in_progress" and current is None:
            current = ch.chapter_name
        elif current is not None and next_ is None and it.status in ("available", "in_progress"):
            next_ = ch.chapter_name

    return LearningPathOut(items=out, current_chapter=current, next_chapter=next_)


@router.get("", response_model=LearningPathOut)
def get_path(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(LearningPathItem).filter(LearningPathItem.user_id == user.id).count()
    if existing == 0:
        lp.generate(db, user.id)
    return _build(db, user.id)


@router.post("/regenerate", response_model=LearningPathOut)
def regenerate(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lp.generate(db, user.id)
    return _build(db, user.id)
