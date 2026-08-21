"""
Response Aggregator.

Combines one or more AgentResponse objects into a single, natural
final reply:
  - Single agent -> use its response directly.
  - Multiple agents -> merge into a clearly-sectioned response,
    removing near-duplicate sentences across agents.
  - Flags escalation when the ComplaintAgent detects escalation
    triggers in the original message.
"""

from dataclasses import dataclass

from backend.agents.base import AgentResponse
from backend.agents.complaint import ComplaintAgent
from backend.rag.vector_store import SearchResult

AGENT_LABELS = {
    "billing": "Billing",
    "technical": "Technical Support",
    "product": "Product Info",
    "complaint": "Complaints",
    "faq": "General",
}


@dataclass
class AggregatedResponse:
    reply: str
    agents_used: list[str]
    sources: list[SearchResult]
    escalated: bool


def _dedupe_sentences(text: str, seen: set[str]) -> str:
    """Drops sentences whose normalized form was already seen in a prior agent's reply."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    kept = []
    for s in sentences:
        norm = s.lower().rstrip(".")
        if norm in seen:
            continue
        seen.add(norm)
        kept.append(s)
    result = ". ".join(kept)
    if result and not result.endswith((".", "!", "?")):
        result += "."
    return result


def aggregate(original_message: str, responses: list[AgentResponse]) -> AggregatedResponse:
    escalated = ComplaintAgent.is_escalation(original_message) or any(
        r.agent_name == "complaint" for r in responses
    )

    all_sources: list[SearchResult] = []
    for r in responses:
        all_sources.extend(r.sources)

    if len(responses) == 1:
        reply = responses[0].text
    else:
        seen_sentences: set[str] = set()
        sections = []
        for r in responses:
            label = AGENT_LABELS.get(r.agent_name, r.agent_name.title())
            deduped = _dedupe_sentences(r.text, seen_sentences)
            if deduped:
                sections.append(f"**{label}:**\n{deduped}")
        reply = "\n\n".join(sections)

    if escalated:
        reply += (
            "\n\nI'm also flagging this for a human specialist to follow up, given the "
            "nature of your message. You should hear from them soon."
        )

    return AggregatedResponse(
        reply=reply,
        agents_used=[r.agent_name for r in responses],
        sources=all_sources,
        escalated=escalated,
    )
