from backend.agents.base import BaseAgent


class FAQAgent(BaseAgent):
    name = "faq"
    description = "Handles general questions about the company, security, and policies."
    preferred_sources = ("general_faq.txt",)
    system_prompt = (
        "You are a general support specialist for NimbusCloud, answering common "
        "questions about the company, security, trials, and account management."
    )
