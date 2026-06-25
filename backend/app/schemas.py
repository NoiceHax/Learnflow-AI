"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


def _strip_str(v: object) -> object:
    return v.strip() if isinstance(v, str) else v


# ---------- Auth ----------
class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("name", "email", "password", mode="before")
    @classmethod
    def strip_fields(cls, v: object) -> object:
        return _strip_str(v)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email", "password", mode="before")
    @classmethod
    def strip_fields(cls, v: object) -> object:
        return _strip_str(v)


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    onboarded: bool

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserOut


# ---------- Catalog ----------
class ChapterOut(BaseModel):
    id: str
    chapter_name: str
    slug: str
    subject_id: str
    prerequisite_id: Optional[str]
    order_index: int
    jee_weightage: int
    description: str
    unlocked: bool = True

    class Config:
        from_attributes = True


class SubjectOut(BaseModel):
    id: str
    name: str
    slug: str
    icon: str
    chapters: list[ChapterOut] = []

    class Config:
        from_attributes = True


# ---------- Quiz engine ----------
class QuestionOption(BaseModel):
    id: str
    text: str


class QuestionOut(BaseModel):
    """Question as delivered to the client. Never includes the answer."""

    id: str
    subject: str
    chapter: str
    chapter_id: str
    difficulty: str
    concept: str
    jee_weightage: int
    type: str
    prompt: str
    options: Optional[list[QuestionOption]] = None
    unit: Optional[str] = None
    ai_generated: bool = False
    is_pyq: bool = False
    pyq_year: Optional[int] = None
    pyq_exam: Optional[str] = None
    correct_answer: Optional[Any] = None
    solution: Optional[str] = None

    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    question_id: str
    answer: Any  # index | [indices] | number | None (skipped)


class QuizSubmission(BaseModel):
    answers: list[AnswerSubmission]
    time_taken: int = 0
    mode: str = "final"  # practice | final


class GradedQuestion(BaseModel):
    question_id: str
    concept: str
    chapter: str
    correct: bool
    your_answer: Any
    correct_answer: Any
    solution: str


class AdaptiveSummary(BaseModel):
    retired_count: int = 0
    replacements_generated: int = 0
    weak_concepts_hit: list[str] = []


class QuizResult(BaseModel):
    score: float
    accuracy: float
    total_questions: int
    correct_count: int
    time_taken: int
    weak_concepts: list[str]
    graded: list[GradedQuestion]
    adaptive: AdaptiveSummary | None = None
    chapter_mastered: bool = False


# ---------- Assessment ----------
class AssessmentSubmission(BaseModel):
    answers: list[AnswerSubmission]
    time_taken: int = 0


class AssessmentResult(BaseModel):
    id: str
    score: float
    chapter_scores: dict[str, float]
    subject_scores: dict[str, float]
    knowledge_map: list[dict[str, Any]]
    total_questions: int
    correct_count: int


# ---------- Learning path ----------
class PathItem(BaseModel):
    chapter_id: str
    chapter_name: str
    slug: str
    subject: str
    position: int
    status: str
    is_weak: bool
    reason: str
    mastery: float
    jee_weightage: int


class LearningPathOut(BaseModel):
    items: list[PathItem]
    current_chapter: Optional[str]
    next_chapter: Optional[str]


# ---------- Mastery / dashboard ----------
class MasteryOut(BaseModel):
    chapter: str
    subject: str
    mastery_score: float
    attempts: int

    class Config:
        from_attributes = True


class ActivityItem(BaseModel):
    kind: str  # quiz | assessment | lesson
    title: str
    detail: str
    score: Optional[float] = None
    timestamp: datetime


class ExamHistoryItem(BaseModel):
    kind: str  # assessment | final_quiz
    id: str
    title: str
    chapter: Optional[str] = None
    chapter_id: Optional[str] = None
    subject: Optional[str] = None
    score: float
    accuracy: float
    correct_count: int
    total_questions: int
    time_taken: Optional[int] = None
    passed: Optional[bool] = None
    timestamp: datetime


class ExamReportOut(BaseModel):
    kind: str  # assessment | final_quiz
    assessment: Optional[AssessmentResult] = None
    quiz_result: Optional[QuizResult] = None
    questions: Optional[list[QuestionOut]] = None
    detail_available: bool = True


class DashboardOut(BaseModel):
    overall_progress: float
    jee_readiness: float = 0.0
    predicted_jee_score: int = 0
    subject_score_breakdown: dict[str, float] = {}
    accuracy: float
    time_spent_hours: float
    subject_mastery: list[dict[str, Any]]
    chapter_mastery: list[dict[str, Any]]
    weak_topics: list[dict[str, Any]]
    strong_topics: list[dict[str, Any]]
    recommended_chapters: list[dict[str, Any]]
    recent_activity: list[ActivityItem]
    chapters_completed: int
    quizzes_attempted: int
    # ---- V2 command-center intelligence ----
    continue_learning: Optional[dict[str, Any]] = None
    next_recommended: list[dict[str, Any]] = []
    weak_areas: list[dict[str, Any]] = []
    strong_areas: list[dict[str, Any]] = []
    revision_queue: list[dict[str, Any]] = []
    recently_completed: list[dict[str, Any]] = []
    ai_recommendations: list[dict[str, Any]] = []
    interpretations: dict[str, str] = {}
    mastery_journey: dict[str, Any] = {}


# ---------- Lessons ----------
class LessonOut(BaseModel):
    id: str
    chapter_id: str
    chapter: str
    content: dict[str, Any]
    generated_by_ai: bool

    class Config:
        from_attributes = True


# ---------- Socrates ----------
class ChatContext(BaseModel):
    subject: Optional[str] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    formulas: list[str] = []
    examples: list[str] = []


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: Optional[str] = None
    chapter_context: Optional[str] = None
    context: Optional[ChatContext] = None


class ChatTurn(BaseModel):
    id: str
    role: Literal["user", "socrates"]
    content: str
    timestamp: datetime
    difficulty: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    powered_by: str  # "nvidia" | "cache" | "fallback"
    difficulty: Optional[str] = None
