"""SQLAlchemy ORM models: the Astra schema.

Mirrors the tables in the spec (users, subjects, chapters, questions,
assessments, quiz_attempts, mastery, learning_paths, lessons, chat_history),
enriched with the columns a real product needs.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=_uuid)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    onboarded = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String(32), primary_key=True, default=_uuid)
    name = Column(String(80), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    icon = Column(String(40), default="atom")
    order_index = Column(Integer, default=0)

    chapters = relationship("Chapter", back_populates="subject", order_by="Chapter.order_index")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(32), primary_key=True, default=_uuid)
    subject_id = Column(String(32), ForeignKey("subjects.id"), nullable=False, index=True)
    chapter_name = Column(String(160), nullable=False)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    prerequisite_id = Column(String(32), ForeignKey("chapters.id"), nullable=True)
    order_index = Column(Integer, default=0)
    jee_weightage = Column(Integer, default=3)
    description = Column(Text, default="")

    subject = relationship("Subject", back_populates="chapters")
    prerequisite = relationship("Chapter", remote_side=[id])


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(32), primary_key=True, default=_uuid)
    subject = Column(String(80), nullable=False)
    chapter = Column(String(160), nullable=False)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False)  # Easy | Medium | Advanced
    concept = Column(String(160), nullable=False)
    jee_weightage = Column(Integer, default=3)
    type = Column(String(30), nullable=False)  # single_correct | multiple_correct | integer | numerical
    prompt = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # [{id, text}] for MCQ types
    correct_answer = Column(JSON, nullable=False)  # index | [indices] | number
    tolerance = Column(Float, nullable=True)  # for numerical
    unit = Column(String(40), nullable=True)
    solution = Column(Text, default="")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    chapter_scores = Column(JSON, default=dict)  # {chapter_slug: percent}
    subject_scores = Column(JSON, default=dict)  # {subject_slug: percent}
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    report = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=False, index=True)
    chapter_name = Column(String(160), default="")
    mode = Column(String(20), default="final", server_default="final", nullable=False)
    score = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    time_taken = Column(Integer, default=0)  # seconds
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    weak_concepts = Column(JSON, default=list)
    report = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class Mastery(Base):
    __tablename__ = "mastery"
    __table_args__ = (UniqueConstraint("user_id", "chapter_id", name="uq_user_chapter"),)

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=False)
    chapter = Column(String(160), nullable=False)
    subject = Column(String(80), default="")
    mastery_score = Column(Float, default=0.0, nullable=False)
    attempts = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class LearningPathItem(Base):
    """One row per (user, chapter). The ordered set of rows IS the learning path."""

    __tablename__ = "learning_paths"
    __table_args__ = (UniqueConstraint("user_id", "chapter_id", name="uq_path_user_chapter"),)

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=False)
    position = Column(Integer, default=0)
    status = Column(String(20), default="locked")  # locked|available|in_progress|completed|mastered
    is_weak = Column(Boolean, default=False)
    reason = Column(String(255), default="")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String(32), primary_key=True, default=_uuid)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=False, index=True)
    chapter = Column(String(160), nullable=False)
    content = Column(JSON, nullable=False)  # structured lesson (theory, examples, ...)
    generated_by_ai = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(32), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    chapter_context = Column(String(160), nullable=True)
    difficulty_level = Column(String(32), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=_now, nullable=False)


class ConceptMastery(Base):
    """Fine-grained, per-concept mastery. Powers adaptive selection, spaced
    repetition and recursive prerequisite remediation."""

    __tablename__ = "concept_mastery"
    __table_args__ = (UniqueConstraint("user_id", "concept", name="uq_user_concept"),)

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    concept = Column(String(160), nullable=False, index=True)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=True)
    subject = Column(String(80), default="")
    ema = Column(Float, default=0.0, nullable=False)  # 0..100 mastery of the concept
    attempts = Column(Integer, default=0)
    correct = Column(Integer, default=0)
    fail_streak = Column(Integer, default=0)  # consecutive misses -> triggers remediation
    last_seen = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class UserQuestionState(Base):
    """Per-user question history. Wrong answers retire a question and trigger replacements."""

    __tablename__ = "user_question_states"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_question"),)

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String(32), ForeignKey("questions.id"), nullable=False, index=True)
    chapter_id = Column(String(32), ForeignKey("chapters.id"), nullable=False, index=True)
    seen_count = Column(Integer, default=0, server_default="0", nullable=False)
    wrong_count = Column(Integer, default=0, server_default="0", nullable=False)
    retired = Column(Boolean, default=False, server_default="false", nullable=False)  # excluded from this user's future quizzes
    last_correct = Column(Boolean, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class LlmCache(Base):
    """Cached LLM outputs: Socrates replies, etc. Questions live in `questions`."""

    __tablename__ = "gemini_cache"  # legacy table name in Neon; do not rename without migration

    cache_key = Column(String(64), primary_key=True)
    cache_type = Column(String(32), nullable=False, index=True)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
