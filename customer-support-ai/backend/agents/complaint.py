from backend.agents.base import BaseAgent

ESCALATION_KEYWORDS = (
    "speak to a manager",
    "speak to a human",
    "human agent",
    "talk to a real person",
    "cancel my subscription",
    "cancel my account",
    "unacceptable",
    "furious",
    "lawsuit",
    "legal action",
    "data loss",
    "lost my data",
    "unauthorized access",
    "hacked",
)


class ComplaintAgent(BaseAgent):
    name = "complaint"
    description = "Handles dissatisfaction, complaints, and escalations."
    preferred_sources = ("complaint_policy.txt",)
    system_prompt = (
        "You are the Complaints specialist for NimbusCloud. Acknowledge the "
        "customer's frustration genuinely, avoid corporate deflection, and always "
        "give a concrete next step or timeline."
    )

    @staticmethod
    def is_escalation(query: str) -> bool:
        q = query.lower()
        return any(keyword in q for keyword in ESCALATION_KEYWORDS)
