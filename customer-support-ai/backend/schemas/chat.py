from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class SourceRef(BaseModel):
    document: str
    snippet: str


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    agents_used: list[str]
    sources: list[SourceRef]
    escalated: bool


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    agents_used: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: str
    title: str
    is_escalated: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailOut(ConversationOut):
    messages: list[MessageOut] = []
