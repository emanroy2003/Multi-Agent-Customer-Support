"""
Agent Router.

Takes the intent detection result and dispatches the query to one or
more specialized agents, running them and collecting their responses.
Supports both single-agent and multi-agent (parallel logical) queries.
"""

from backend.agents.base import AgentResponse
from backend.agents.billing import BillingAgent
from backend.agents.complaint import ComplaintAgent
from backend.agents.faq import FAQAgent
from backend.agents.intent_detector import detect_intents
from backend.agents.product import ProductAgent
from backend.agents.technical import TechnicalAgent
from backend.utils.logger import logger

AGENT_REGISTRY = {
    "billing": BillingAgent(),
    "technical": TechnicalAgent(),
    "product": ProductAgent(),
    "complaint": ComplaintAgent(),
    "faq": FAQAgent(),
}

MAX_AGENTS_PER_QUERY = 3


def route_and_run(message: str, history: str = "") -> list[AgentResponse]:
    intent = detect_intents(message)
    agent_names = intent.agents[:MAX_AGENTS_PER_QUERY]

    logger.info(f"Routed message to agents: {agent_names} (scores={intent.scores})")

    responses: list[AgentResponse] = []
    for name in agent_names:
        agent = AGENT_REGISTRY[name]
        responses.append(agent.handle(message, history=history))

    return responses
