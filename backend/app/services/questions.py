"""Map ORM questions to API responses."""
from ..models import Question
from ..schemas import QuestionOut


def question_to_out(q: Question) -> QuestionOut:
    data = QuestionOut.model_validate(q)
    return data.model_copy(update={"ai_generated": q.concept.startswith("[AI] ")})
