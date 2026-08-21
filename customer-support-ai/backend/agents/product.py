from backend.agents.base import BaseAgent


class ProductAgent(BaseAgent):
    name = "product"
    description = "Handles questions about features, plans, and how the product works."
    preferred_sources = ("product_info.txt",)
    system_prompt = (
        "You are the Product specialist for NimbusCloud. You help customers understand "
        "features, plan tiers, and how to get the most out of the product."
    )
