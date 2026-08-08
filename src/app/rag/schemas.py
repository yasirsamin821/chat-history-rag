from pydantic import BaseModel


class Turn(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Turn] = []


class ChatResponse(BaseModel):
    route: str
    answer: str
    sources: list[str]
    standalone_question: str
