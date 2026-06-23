"""Dashboard intelligence: turns raw progress into a mentor's command center.

Produces everything the redesigned dashboard needs: what to continue, what's
recommended next (prerequisite-aware), weak areas ranked by how much they block,
a spaced-repetition revision queue, recursive remediation when a concept keeps
failing, and human-readable recommendations + analytics interpretations.

All deterministic and data-driven (no LLM latency on dashboard load).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ..models import Assessment, Chapter, ConceptMastery, LearningPathItem, Mastery, QuizAttempt, Subject
from . import concepts
from .mastery import MASTER_THRESHOLD, WEAK_THRESHOLD
from .mastery_journey import build_mastery_journey


def _days_since(dt: datetime | None) -> float:
    if dt is None:
        return 999.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0)


def _blocked_chapter_names(prereq_chain: dict[str, str | None], chapters: dict[str, Chapter], cid: str) -> list[str]:
    names: list[str] = []
    for other in prereq_chain:
        if other == cid:
            continue
        cur = prereq_chain.get(other)
        guard = 0
        while cur and guard < 50:
            if cur == cid:
                names.append(chapters[other].chapter_name)
                break
            cur = prereq_chain.get(cur)
            guard += 1
    return names


def build_dashboard(db: Session, user_id: str) -> dict[str, Any]:
    masteries = db.query(Mastery).filter(Mastery.user_id == user_id).all()
    concept_rows = db.query(ConceptMastery).filter(ConceptMastery.user_id == user_id).all()
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.mode == "final")
        .order_by(QuizAttempt.created_at.desc())
        .all()
    )
    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == user_id)
        .order_by(Assessment.created_at.desc())
        .all()
    )
    subjects = {s.id: s for s in db.query(Subject).all()}
    chapters = {c.id: c for c in db.query(Chapter).all()}
    path_items = (
        db.query(LearningPathItem)
        .filter(LearningPathItem.user_id == user_id)
        .order_by(LearningPathItem.position)
        .all()
    )

    prereq_chain = {c.id: c.prerequisite_id for c in chapters.values()}
    concept_ema = {r.concept: r.ema for r in concept_rows}

    def is_weak_concept(c: str) -> bool:
        return concept_ema.get(c, 100.0) < WEAK_THRESHOLD

    # ---- headline metrics ----
    overall = round(sum(m.mastery_score for m in masteries) / len(masteries), 1) if masteries else 0.0
    chapters_completed = sum(1 for m in masteries if m.mastery_score >= MASTER_THRESHOLD)
    tot_correct = sum(a.correct_count for a in attempts) + sum(a.correct_count for a in assessments)
    tot_q = sum(a.total_questions for a in attempts) + sum(a.total_questions for a in assessments)
    accuracy = round(100.0 * tot_correct / tot_q, 1) if tot_q else 0.0
    time_spent_hours = round(sum(a.time_taken for a in attempts) / 3600.0, 1)

    # ---- subject & chapter mastery ----
    by_subject: dict[str, list[float]] = defaultdict(list)
    for m in masteries:
        ch = chapters.get(m.chapter_id)
        if ch:
            by_subject[ch.subject_id].append(m.mastery_score)
    subject_mastery = [
        {
            "subject": subj.name,
            "slug": subj.slug,
            "mastery": round(sum(by_subject[sid]) / len(by_subject[sid]), 1) if by_subject.get(sid) else 0.0,
        }
        for sid, subj in sorted(subjects.items(), key=lambda kv: kv[1].order_index)
    ]
    chapter_mastery = [
        {"chapter": m.chapter, "subject": m.subject, "mastery": round(m.mastery_score, 1)}
        for m in sorted(masteries, key=lambda m: m.mastery_score, reverse=True)
    ]

    weak_sorted = sorted(masteries, key=lambda m: m.mastery_score)
    weak_topics = [
        {"chapter": m.chapter, "subject": m.subject, "mastery": round(m.mastery_score, 1)}
        for m in weak_sorted if m.mastery_score < WEAK_THRESHOLD
    ][:6]
    strong_topics = [
        {"chapter": m.chapter, "subject": m.subject, "mastery": round(m.mastery_score, 1)}
        for m in reversed(weak_sorted) if m.mastery_score >= MASTER_THRESHOLD
    ][:6]

    # ---- continue / next recommended (from prerequisite-aware path) ----
    continue_learning: dict[str, Any] | None = None
    next_recommended: list[dict[str, Any]] = []
    for it in path_items:
        ch = chapters.get(it.chapter_id)
        if not ch:
            continue
        subj = subjects.get(ch.subject_id)
        mastery_val = next((m.mastery_score for m in masteries if m.chapter_id == ch.id), 0.0)
        payload = {
            "chapter_id": ch.id,
            "chapter": ch.chapter_name,
            "subject": subj.name if subj else "",
            "mastery": round(mastery_val, 1),
            "reason": it.reason,
            "is_weak": it.is_weak,
        }
        if it.status == "in_progress" and continue_learning is None:
            continue_learning = payload
        elif it.status == "available" and len(next_recommended) < 4:
            next_recommended.append(payload)
    if continue_learning is None and next_recommended:
        continue_learning = next_recommended.pop(0)

    # ---- weak areas ranked by severity, with remediation ----
    weak_areas: list[dict[str, Any]] = []
    for m in weak_sorted:
        if m.mastery_score >= WEAK_THRESHOLD:
            continue
        ch = chapters.get(m.chapter_id)
        if not ch:
            continue
        blocked = _blocked_chapter_names(prereq_chain, chapters, ch.id)
        severity = round((100.0 - m.mastery_score) / 100.0 * ch.jee_weightage * (1 + len(blocked)), 2)
        remediation = _remediation_for_chapter(ch, concept_rows, chapters, db, is_weak_concept)
        weak_areas.append(
            {
                "chapter_id": ch.id,
                "chapter": ch.chapter_name,
                "subject": m.subject,
                "mastery": round(m.mastery_score, 1),
                "severity": severity,
                "blocks": len(blocked),
                "blocked": blocked[:3],
                "remediation": remediation,
            }
        )
    weak_areas.sort(key=lambda w: w["severity"], reverse=True)
    weak_areas = weak_areas[:6]

    strong_areas = strong_topics

    # ---- revision queue (spaced repetition + decay) ----
    revision_queue = _revision_queue(concept_rows, chapters)

    # ---- recently completed topics ----
    recently_completed: list[dict[str, Any]] = []
    seen_ch: set[str] = set()
    for a in attempts:
        if a.chapter_id in seen_ch:
            continue
        seen_ch.add(a.chapter_id)
        ch = chapters.get(a.chapter_id)
        recently_completed.append(
            {
                "chapter_id": a.chapter_id,
                "chapter": a.chapter_name,
                "subject": (subjects.get(ch.subject_id).name if ch and ch.subject_id in subjects else ""),
                "score": a.score,
                "timestamp": a.created_at,
            }
        )
        if len(recently_completed) >= 6:
            break

    # ---- recent activity (quizzes + assessments) ----
    recent_activity: list[dict[str, Any]] = []
    for a in attempts[:10]:
        recent_activity.append({
            "kind": "quiz", "title": f"Final Quiz · {a.chapter_name}",
            "detail": f"{a.correct_count}/{a.total_questions} correct · {a.accuracy:.0f}% accuracy",
            "score": a.score, "timestamp": a.created_at,
        })
    for a in assessments[:3]:
        recent_activity.append({
            "kind": "assessment", "title": "Initial Assessment",
            "detail": f"{a.correct_count}/{a.total_questions} correct across all subjects",
            "score": a.score, "timestamp": a.created_at,
        })
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = recent_activity[:8]

    # ---- AI recommendations + interpretations ----
    ai_recommendations = _recommendations(continue_learning, weak_areas, strong_areas, revision_queue)
    interpretations = _interpretations(accuracy, time_spent_hours, weak_areas, subject_mastery, tot_q)
    mastery_journey = build_mastery_journey(db, user_id)

    return {
        "overall_progress": overall,
        "accuracy": accuracy,
        "time_spent_hours": time_spent_hours,
        "subject_mastery": subject_mastery,
        "chapter_mastery": chapter_mastery,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "recommended_chapters": next_recommended,
        "recent_activity": recent_activity,
        "chapters_completed": chapters_completed,
        "quizzes_attempted": len(attempts),
        "continue_learning": continue_learning,
        "next_recommended": next_recommended,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
        "revision_queue": revision_queue,
        "recently_completed": recently_completed,
        "ai_recommendations": ai_recommendations,
        "interpretations": interpretations,
        "mastery_journey": mastery_journey,
    }


def _remediation_for_chapter(ch, concept_rows, chapters, db, is_weak_concept) -> dict[str, Any] | None:
    """If a concept in this chapter keeps failing, decompose it into prerequisites."""
    failing = [r for r in concept_rows if r.chapter_id == ch.id and (r.fail_streak >= 2 or r.ema < 45)]
    if not failing:
        return None
    worst = min(failing, key=lambda r: r.ema)
    steps = concepts.remediation_steps(worst.concept, is_weak_concept)
    if not steps:
        return None
    slug_to_chapter = {c.slug: c for c in chapters.values()}
    step_objs = []
    for s in steps:
        slug = concepts.chapter_of(s)
        target = slug_to_chapter.get(slug) if slug else None
        step_objs.append({
            "concept": s,
            "chapter": target.chapter_name if target else "Fundamentals",
            "chapter_id": target.id if target else None,
        })
    return {"concept": worst.concept, "steps": step_objs}


def _revision_queue(concept_rows, chapters) -> list[dict[str, Any]]:
    candidates = []
    for r in concept_rows:
        if r.attempts <= 0:
            continue
        days = _days_since(r.last_seen)
        due = r.ema < 70 or r.fail_streak >= 1 or days > 2
        if not due:
            continue
        if r.fail_streak >= 2:
            reason = "Missed repeatedly, needs reinforcement"
        elif days > 3:
            reason = f"Not practised in {int(days)} days"
        elif r.ema < 60:
            reason = "Accuracy slipping"
        else:
            reason = "Due for spaced review"
        ch = chapters.get(r.chapter_id)
        priority = r.fail_streak * 100 + (100 - r.ema) + min(days, 30)
        candidates.append({
            "concept": r.concept,
            "chapter": ch.chapter_name if ch else "",
            "chapter_id": r.chapter_id,
            "subject": r.subject,
            "mastery": round(r.ema, 1),
            "reason": reason,
            "_p": priority,
        })
    candidates.sort(key=lambda x: x["_p"], reverse=True)
    for c in candidates:
        c.pop("_p", None)
    return candidates[:6]


def _recommendations(continue_learning, weak_areas, strong_areas, revision_queue) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []

    # 1. Recursive remediation has top priority.
    for w in weak_areas:
        rem = w.get("remediation")
        if rem and rem.get("steps"):
            first = rem["steps"][0]
            recs.append({
                "kind": "remediation",
                "title": f"Rebuild the foundation for {w['chapter']}",
                "text": (
                    f"You keep slipping on {rem['concept']}. Step back to "
                    f"{first['concept']} ({first['chapter']}) to rebuild the fundamentals, then return."
                ),
                "action_label": f"Study {first['chapter']}",
                "action_chapter_id": first.get("chapter_id"),
            })
            break

    # 2. Highest-blocking weak area.
    blockers = [w for w in weak_areas if w["blocks"] > 0]
    if blockers:
        w = blockers[0]
        blocked_txt = ", ".join(w["blocked"]) if w["blocked"] else "later chapters"
        recs.append({
            "kind": "unlock",
            "title": f"Prioritise {w['chapter']}",
            "text": (
                f"This is limiting {blocked_txt}. Improving {w['chapter']} will unlock "
                f"{w['blocks']} future chapter{'s' if w['blocks'] != 1 else ''}."
            ),
            "action_label": f"Practise {w['chapter']}",
            "action_chapter_id": w["chapter_id"],
        })

    # 3. Continue current focus.
    if continue_learning:
        recs.append({
            "kind": "continue",
            "title": f"Continue {continue_learning['chapter']}",
            "text": f"You're at {continue_learning['mastery']}% mastery here. Keep the momentum going.",
            "action_label": "Resume",
            "action_chapter_id": continue_learning["chapter_id"],
        })

    # 4. Push strong areas further.
    if strong_areas:
        s = strong_areas[0]
        recs.append({
            "kind": "advance",
            "title": f"Level up {s['chapter']}",
            "text": f"You've mastered {s['chapter']} ({s['mastery']}%). Try advanced, multi-concept problems to push further.",
            "action_label": "Advanced practice",
            "action_chapter_id": None,
        })

    # 5. Spaced revision.
    if revision_queue:
        r = revision_queue[0]
        recs.append({
            "kind": "revise",
            "title": f"Revise {r['concept']}",
            "text": f"{r['reason']} in {r['chapter']}. A quick revision quiz will lock it back in.",
            "action_label": f"Revise {r['chapter']}",
            "action_chapter_id": r["chapter_id"],
        })

    return recs[:5]


def _interpretations(accuracy, hours, weak_areas, subject_mastery, tot_q) -> dict[str, str]:
    if tot_q == 0:
        return {
            "accuracy": "Take a few quizzes and the assessment to start tracking your accuracy.",
            "time": "Build a steady study habit. Short daily sessions beat occasional marathons.",
            "weak": "Once you've practised, your weakest topics and what they block will appear here.",
            "radar": "Your subject strengths will be mapped after you complete some practice.",
        }

    if accuracy >= 80:
        acc = f"Your accuracy ({accuracy}%) is strong. Focus on reducing careless mistakes rather than chasing speed."
    elif accuracy >= 60:
        acc = f"Solid accuracy ({accuracy}%). Tightening up weak concepts will push you into the top band."
    else:
        acc = f"Accuracy ({accuracy}%) needs work. Slow down and revisit fundamentals before raising difficulty."

    time_txt = (
        f"You've logged {hours}h of focused practice. Consistent daily study matters more than long sessions. "
        "aim for a little every day."
    )

    if weak_areas:
        w = weak_areas[0]
        if w["blocked"]:
            weak_txt = (
                f"{w['chapter']} is your priority. It's limiting {', '.join(w['blocked'])}. "
                "Improving it will unlock several future chapters."
            )
        else:
            weak_txt = f"{w['chapter']} is your weakest area at {w['mastery']}%. Spend your next sessions reinforcing it."
    else:
        weak_txt = "No major weak spots right now. Keep reinforcing to stay sharp."

    rated = [s for s in subject_mastery if s["mastery"] > 0]
    if rated:
        strongest = max(rated, key=lambda s: s["mastery"])
        weakest = min(rated, key=lambda s: s["mastery"])
        if strongest["subject"] == weakest["subject"]:
            radar = f"{strongest['subject']} is tracking at {strongest['mastery']}%. Keep building across the other subjects."
        else:
            radar = (
                f"{strongest['subject']} is your strongest subject ({strongest['mastery']}%), "
                f"while {weakest['subject']} ({weakest['mastery']}%) needs the most revision."
            )
    else:
        radar = "Your subject strengths will be mapped after you complete some practice."

    return {"accuracy": acc, "time": time_txt, "weak": weak_txt, "radar": radar}
