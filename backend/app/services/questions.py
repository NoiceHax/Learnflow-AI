"""Map ORM questions to API responses."""
from ..models import Question
from ..schemas import QuestionOut


def question_to_out(q: Question, include_answer: bool = False) -> QuestionOut:
    data = QuestionOut.model_validate(q)
    update_dict = {"ai_generated": q.concept.startswith("[AI] ")}
    if not include_answer:
        update_dict["correct_answer"] = None
        update_dict["solution"] = None
    return data.model_copy(update=update_dict)
