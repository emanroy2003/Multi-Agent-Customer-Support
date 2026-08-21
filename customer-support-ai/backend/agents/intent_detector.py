"""
Intent Detection Agent.

Classifies a customer message into one or more of the five support
domains (billing, technical, product, complaint, faq) using weighted
keyword matching. This is deliberately dependency-free (no LLM call
needed) so routing is fast, deterministic, and testable offline.

Multi-label by design: a message like "I paid yesterday but my
Premium account is still locked" scores high on both "billing" and
"technical" keywords and should route to both agents.
"""

from dataclasses import dataclass

KEYWORDS: dict[str, list[str]] = {
    "billing": [
        "charge", "charged", "payment", "paid", "invoice", "refund", "billing",
        "subscription", "price", "pricing", "plan cost", "credit card", "receipt",
        "downgrade", "upgrade", "prorated", "double charged", "overcharged",
    ],
    "technical": [
        "error", "bug", "not working", "broken", "crash", "login", "log in",
        "locked", "password", "reset", "api", "401", "429", "slow", "sync",
        "sync issue", "loading", "can't access", "cannot access", "unauthorized",
    ],
    "product": [
        "feature", "features", "how do i", "how does", "plan", "tier",
        "compare", "included", "sso", "integration", "mobile app", "automation",
        "roadmap", "storage limit",
    ],
    "complaint": [
        "unhappy", "frustrated", "angry", "disappointed", "terrible", "worst",
        "complain", "complaint", "manager", "human agent", "unacceptable",
        "furious", "cancel", "refund my money", "never again",
    ],
    "faq": [
        "support hours", "contact support", "security", "data secure", "trial",
        "free trial", "delete my account", "server location", "gdpr", "encryption",
    ],
}

DEFAULT_THRESHOLD = 1  # at least 1 keyword hit required to route to an agent


@dataclass
class IntentResult:
    agents: list[str]
    scores: dict[str, int]


def detect_intents(message: str, threshold: int = DEFAULT_THRESHOLD) -> IntentResult:
    text = message.lower()
    scores: dict[str, int] = {}

    for agent_name, keywords in KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[agent_name] = score

    matched = [name for name, score in scores.items() if score >= threshold]

    # Fallback: nothing matched strongly -> route to FAQ as a safe general default
    if not matched:
        matched = ["faq"]
        scores.setdefault("faq", 0)

    # Sort by score descending so the primary agent is first
    matched.sort(key=lambda name: scores.get(name, 0), reverse=True)

    return IntentResult(agents=matched, scores=scores)
