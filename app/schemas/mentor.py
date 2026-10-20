from typing import Annotated, Literal

from pydantic import Field

from app.schemas.common import CamelModel, XpBalance


class AIMessage(CamelModel):
    id: str
    role: Literal["ai", "user"]
    text: str
    timestamp: str


class ProblemContextRef(CamelModel):
    kind: Literal["problem"]
    problem_slug: str


class LessonContextRef(CamelModel):
    kind: Literal["lesson"]
    lesson_id: str
    # Current lesson step, e.g. "concept", "tryit", "quiz".
    step: str | None = None


ContextRef = Annotated[ProblemContextRef | LessonContextRef, Field(discriminator="kind")]


class AskRequest(CamelModel):
    context: ContextRef
    question: str = Field(min_length=1, max_length=1000)
    # How many questions were asked before in this conversation, so repeated hint requests reveal the next hint.
    turn: int = Field(default=0, ge=0)


class AskResponse(CamelModel):
    question: AIMessage
    answer: AIMessage
    cost: int
    balance: XpBalance


class SuggestionsResponse(CamelModel):
    suggestions: list[str]
