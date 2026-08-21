"""
Chat Service.

Orchestrates a full chat turn:
  1. Load or create the conversation.
  2. Build a short history string for context.
  3. Route the message to the right agent(s) and run them.
  4. Aggregate responses into one final reply.
  5. Persist both the user message and the assistant reply.
"""

import json

from sqlalchemy.orm import Session

from backend.agents.router import route_and_run
from backend.models.conversation import Conversation, Message
from backend.schemas.chat import ChatResponse, SourceRef
from backend.services.aggregator import aggregate
from backend.utils.logger import logger

MAX_HISTORY_MESSAGES = 6


def _get_or_create_conversation(db: Session, user_id: str, conversation_id: str | None) -> Conversation:
    if conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )
        if conversation:
            return conversation

    conversation = Conversation(user_id=user_id, title="New Conversation")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def _build_history(conversation: Conversation) -> str:
    recent = conversation.messages[-MAX_HISTORY_MESSAGES:]
    lines = [f"{m.role.capitalize()}: {m.content}" for m in recent]
    return "\n".join(lines)


def _maybe_set_title(conversation: Conversation, first_message: str):
    if conversation.title == "New Conversation":
        conversation.title = (first_message[:50] + "...") if len(first_message) > 50 else first_message


def handle_chat_turn(db: Session, user_id: str, message: str, conversation_id: str | None) -> ChatResponse:
    conversation = _get_or_create_conversation(db, user_id, conversation_id)
    history = _build_history(conversation)

    if not conversation.messages:
        _maybe_set_title(conversation, message)

    user_msg = Message(conversation_id=conversation.id, role="user", content=message)
    db.add(user_msg)

    agent_responses = route_and_run(message, history=history)
    aggregated = aggregate(message, agent_responses)

    if aggregated.escalated:
        conversation.is_escalated = True

    source_refs = [
        SourceRef(document=s.source, snippet=s.chunk[:200]) for s in aggregated.sources[:5]
    ]

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=aggregated.reply,
        agents_used=",".join(aggregated.agents_used),
        sources=json.dumps([s.model_dump() for s in source_refs]),
    )
    db.add(assistant_msg)
    db.commit()

    logger.info(
        f"Chat turn complete | conversation={conversation.id} agents={aggregated.agents_used} "
        f"escalated={aggregated.escalated}"
    )

    return ChatResponse(
        conversation_id=conversation.id,
        reply=aggregated.reply,
        agents_used=aggregated.agents_used,
        sources=source_refs,
        escalated=aggregated.escalated,
    )
