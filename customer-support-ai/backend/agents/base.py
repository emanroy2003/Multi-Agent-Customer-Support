"""
Base class for all specialized support agents.

Each agent:
  1. Retrieves relevant knowledge base chunks via RAG (optionally
     filtered to documents relevant to that agent's domain).
  2. Builds a domain-specific prompt.
  3. Calls the configured LLM to generate a grounded response.
"""

from dataclasses import dataclass, field

from backend.rag.vector_store import SearchResult, vector_store
from backend.services.llm import generate_response


@dataclass
class AgentResponse:
    agent_name: str
    text: str
    sources: list[SearchResult] = field(default_factory=list)
    confidence: float = 0.0


class BaseAgent:
    name: str = "base"
    description: str = "Base agent"
    # Preferred source filenames for this agent's domain (used to bias retrieval)
    preferred_sources: tuple[str, ...] = ()
    system_prompt: str = "You are a helpful customer support assistant."

    def retrieve_context(self, query: str, top_k: int = 4) -> list[SearchResult]:
        results = vector_store.search(query, top_k=top_k * 2 if self.preferred_sources else top_k)
        if not self.preferred_sources:
            return results[:top_k]

        preferred = [r for r in results if r.source in self.preferred_sources]
        other = [r for r in results if r.source not in self.preferred_sources]
        return (preferred + other)[:top_k]

    def build_prompt(self, query: str, context: list[SearchResult], history: str = "") -> str:
        context_block = (
            "\n\n".join(f"[Source: {r.source}]\n{r.chunk}" for r in context)
            if context
            else "No relevant knowledge base articles were found."
        )
        history_block = f"\nConversation so far:\n{history}\n" if history else ""

        return f"""{history_block}
Customer question: {query}

Relevant knowledge base context:
{context_block}

Instructions: Answer using ONLY the information in the context above. If the
context does not contain the answer, say so honestly instead of guessing.
Be concise, warm, and specific. Do not invent policies, prices, or facts
that are not present in the context."""

    def handle(self, query: str, history: str = "") -> AgentResponse:
        context = self.retrieve_context(query)
        prompt = self.build_prompt(query, context, history)
        text = generate_response(system_prompt=self.system_prompt, user_prompt=prompt)
        confidence = min(1.0, sum(r.score for r in context) / max(len(context), 1)) if context else 0.3
        return AgentResponse(agent_name=self.name, text=text, sources=context, confidence=confidence)
