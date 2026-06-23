"""Build the Mastery Journey graph: adaptive nodes + revision inserts from live data."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from ..models import Chapter, ConceptMastery, LearningPathItem, Lesson, Mastery, QuizAttempt, Subject
from .concepts import remediation_steps
from .mastery import MASTER_THRESHOLD, WEAK_THRESHOLD


def _node_state(path_status: str, mastery: float) -> str:
    if path_status == "locked":
        return "locked"
    if path_status == "mastered" or mastery >= MASTER_THRESHOLD:
        return "mastered"
    if path_status == "in_progress":
        return "in_progress"
    if mastery < WEAK_THRESHOLD:
        return "revision"
    if path_status in ("available", "completed"):
        return "available"
    return "available"


def _chapter_detail(
    db: Session,
    user_id: str,
    chapter: Chapter,
    subject_name: str,
    mastery_val: float,
    concept_rows: list[ConceptMastery],
    attempts: list[QuizAttempt],
) -> dict[str, Any]:
    ch_attempts = [a for a in attempts if a.chapter_id == chapter.id]
    quiz_count = len(ch_attempts)
    avg_score = round(sum(a.score for a in ch_attempts) / quiz_count, 1) if quiz_count else None
    time_sec = sum(a.time_taken for a in ch_attempts)
    weak_in_chapter = [c for c in concept_rows if c.chapter_id == chapter.id and c.ema < WEAK_THRESHOLD]

    lesson = db.query(Lesson).filter(Lesson.chapter_id == chapter.id).first()
    common_mistakes: list[str] = []
    if lesson and isinstance(lesson.content, dict):
        common_mistakes = list(lesson.content.get("common_mistakes") or [])[:4]

    recommendation = ""
    if weak_in_chapter:
        worst = min(weak_in_chapter, key=lambda c: c.ema)
        recommendation = (
            f"Review {worst.concept.replace('[AI] ', '')} before continuing. "
            f"currently at {round(worst.ema, 0):.0f}% mastery."
        )
    elif mastery_val < MASTER_THRESHOLD:
        recommendation = "Complete the lesson and take a practice quiz to strengthen this chapter."
    else:
        recommendation = "Strong foundation. Advance to the next concept when ready."

    m_row = (
        db.query(Mastery)
        .filter(Mastery.user_id == user_id, Mastery.chapter_id == chapter.id)
        .one_or_none()
    )

    return {
        "quiz_attempts": quiz_count,
        "average_score": avg_score,
        "lessons_completed": 1 if lesson else 0,
        "time_spent_minutes": round(time_sec / 60, 1),
        "common_mistakes": common_mistakes,
        "recommendation": recommendation,
        "weak_concepts": [
            {"concept": c.concept.replace("[AI] ", ""), "mastery": round(c.ema, 1)}
            for c in sorted(weak_in_chapter, key=lambda x: x.ema)[:5]
        ],
        "chapter_attempts": m_row.attempts if m_row else 0,
    }


def build_mastery_journey(db: Session, user_id: str) -> dict[str, Any]:
    path_items = (
        db.query(LearningPathItem)
        .filter(LearningPathItem.user_id == user_id)
        .order_by(LearningPathItem.position)
        .all()
    )
    if not path_items:
        return {
            "nodes": [],
            "edges": [],
            "focus_node_id": None,
            "current_subject": None,
            "current_module": None,
            "stats": {"mastered": 0, "in_progress": 0, "revision": 0, "locked": 0},
        }

    chapters = {c.id: c for c in db.query(Chapter).all()}
    subjects = {s.id: s for s in db.query(Subject).all()}
    mastery_map = {
        m.chapter_id: m.mastery_score
        for m in db.query(Mastery).filter(Mastery.user_id == user_id).all()
    }
    concept_rows = db.query(ConceptMastery).filter(ConceptMastery.user_id == user_id).all()
    concepts_by_chapter: dict[str, list[ConceptMastery]] = defaultdict(list)
    for r in concept_rows:
        if r.chapter_id:
            concepts_by_chapter[r.chapter_id].append(r)

    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.mode == "final")
        .all()
    )

    def is_weak_concept(c: str) -> bool:
        row = next((r for r in concept_rows if r.concept == c or r.concept.endswith(c)), None)
        return row is not None and (row.ema < WEAK_THRESHOLD or row.fail_streak >= 2)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    prev_id: str | None = None
    focus_id: str | None = None
    stats = {"mastered": 0, "in_progress": 0, "revision": 0, "locked": 0, "available": 0}
    current_subject: str | None = None
    current_module: str | None = None

    for item in path_items:
        ch = chapters.get(item.chapter_id)
        if ch is None:
            continue
        subj = subjects.get(ch.subject_id)
        subject_name = subj.name if subj else ""
        mastery_val = round(mastery_map.get(ch.id, 0.0), 1)
        state = _node_state(item.status, mastery_val)
        stats[state] = stats.get(state, 0) + 1

        if item.status == "in_progress":
            current_subject = subject_name
            current_module = ch.chapter_name
            focus_id = f"ch-{ch.id}"

        # Adaptive inserts: revision nodes before weak in-progress chapters
        if item.status in ("in_progress", "available") and mastery_val < MASTER_THRESHOLD:
            weak_cm = [
                c for c in concepts_by_chapter.get(ch.id, [])
                if c.ema < WEAK_THRESHOLD or c.fail_streak >= 2
            ]
            if not weak_cm:
                ch_weak = [c for c in concept_rows if c.chapter_id == ch.id and c.ema < WEAK_THRESHOLD]
                if ch_weak:
                    worst = min(ch_weak, key=lambda c: c.ema)
                    steps = remediation_steps(worst.concept.replace("[AI] ", ""), is_weak_concept)
                    for step in steps[:2]:
                        weak_cm.append(
                            {
                                "concept": step,
                                "ema": 45.0,
                                "fail_streak": 2,
                                "chapter_id": ch.id,
                            }
                        )

            for cm in sorted(weak_cm, key=lambda c: c.ema if hasattr(c, "ema") else c["ema"])[:2]:
                concept_clean = (
                    cm.concept.replace("[AI] ", "")
                    if hasattr(cm, "concept")
                    else str(cm["concept"])
                )
                ema_val = cm.ema if hasattr(cm, "ema") else float(cm["ema"])
                rev_id = f"rev-{ch.id}-{concept_clean.lower().replace(' ', '-')[:40]}"
                if any(n["id"] == rev_id for n in nodes):
                    continue
                rev_node = {
                    "id": rev_id,
                    "type": "revision",
                    "label": concept_clean,
                    "subtitle": "Revision",
                    "state": "revision",
                    "mastery": round(ema_val, 1),
                    "chapter_id": ch.id,
                    "chapter_name": ch.chapter_name,
                    "subject": subject_name,
                    "slug": ch.slug,
                    "inserted": True,
                    "detail": {
                        "quiz_attempts": 0,
                        "average_score": None,
                        "lessons_completed": 0,
                        "time_spent_minutes": 0,
                        "common_mistakes": [],
                        "recommendation": f"Strengthen {concept_clean} before retesting {ch.chapter_name}.",
                        "weak_concepts": [{"concept": concept_clean, "mastery": round(ema_val, 1)}],
                        "chapter_attempts": 0,
                    },
                }
                nodes.append(rev_node)
                stats["revision"] += 1
                if prev_id:
                    edges.append({"from": prev_id, "to": rev_id})
                prev_id = rev_id
                focus_id = rev_id

            if weak_cm and item.status == "in_progress":
                retest_id = f"retest-{ch.id}"
                retest_node = {
                    "id": retest_id,
                    "type": "retest",
                    "label": f"{ch.chapter_name} Retest",
                    "subtitle": "Practice",
                    "state": "in_progress" if item.status == "in_progress" else "available",
                    "mastery": mastery_val,
                    "chapter_id": ch.id,
                    "chapter_name": ch.chapter_name,
                    "subject": subject_name,
                    "slug": ch.slug,
                    "inserted": True,
                    "detail": _chapter_detail(db, user_id, ch, subject_name, mastery_val, concept_rows, attempts),
                }
                nodes.append(retest_node)
                if prev_id:
                    edges.append({"from": prev_id, "to": retest_id})
                prev_id = retest_id
                if item.status == "in_progress":
                    focus_id = retest_id
                continue  # skip duplicate chapter node when retest path active

        ch_id = f"ch-{ch.id}"
        detail = _chapter_detail(db, user_id, ch, subject_name, mastery_val, concept_rows, attempts)
        node = {
            "id": ch_id,
            "type": "chapter",
            "label": ch.chapter_name,
            "subtitle": subject_name,
            "state": state,
            "mastery": mastery_val,
            "chapter_id": ch.id,
            "chapter_name": ch.chapter_name,
            "subject": subject_name,
            "slug": ch.slug,
            "inserted": False,
            "reason": item.reason,
            "detail": detail,
        }
        nodes.append(node)
        if prev_id:
            edges.append({"from": prev_id, "to": ch_id})
        prev_id = ch_id

    return {
        "nodes": nodes,
        "edges": edges,
        "focus_node_id": focus_id,
        "current_subject": current_subject,
        "current_module": current_module,
        "stats": stats,
    }
