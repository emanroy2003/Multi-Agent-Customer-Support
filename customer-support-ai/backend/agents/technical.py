from backend.agents.base import BaseAgent


class TechnicalAgent(BaseAgent):
    name = "technical"
    description = "Handles bugs, errors, login issues, performance problems, and API issues."
    preferred_sources = ("technical_support.txt",)
    system_prompt = (
        "You are the Technical Support specialist for NimbusCloud. You help customers "
        "troubleshoot login issues, errors, performance problems, and API/integration "
        "issues. Give clear, actionable steps."
    )
