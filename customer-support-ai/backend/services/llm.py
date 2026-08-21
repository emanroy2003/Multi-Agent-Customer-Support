"""
Configurable LLM provider service.

Reads LLM_PROVIDER from settings ("openai" or "anthropic") and routes
generation calls accordingly. If no API key is configured for the
selected provider, falls back to a deterministic, context-grounded
response so the system remains fully functional (e.g. for local
testing or demos) without ever fabricating unsupported claims.
"""

from backend.config import settings
from backend.utils.logger import logger


def _generate_openai(system_prompt: str, user_prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return completion.choices[0].message.content.strip()


def _generate_anthropic(system_prompt: str, user_prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text").strip()


def _fallback_response(user_prompt: str) -> str:
    """
    Deterministic, context-grounded fallback used when no LLM API key is
    configured. Extracts the retrieved context straight out of the prompt
    and presents it directly, so the answer is still accurate and never
    hallucinated -- just less conversationally polished than an LLM.
    """
    marker = "Relevant knowledge base context:\n"
    if marker in user_prompt:
        context = user_prompt.split(marker, 1)[1].split("\n\nInstructions:")[0].strip()
    else:
        context = ""

    if not context or context == "No relevant knowledge base articles were found.":
        return (
            "I couldn't find specific information about that in our knowledge base. "
            "Could you provide a bit more detail, or would you like me to escalate this "
            "to a human specialist?"
        )

    return (
        "Here's what I found that should help:\n\n"
        f"{context}\n\n"
        "(Note: this response is running in fallback mode because no LLM API key is "
        "configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env for "
        "fully conversational answers.)"
    )


def generate_response(system_prompt: str, user_prompt: str) -> str:
    provider = settings.llm_provider

    try:
        if provider == "openai" and settings.openai_api_key:
            return _generate_openai(system_prompt, user_prompt)
        if provider == "anthropic" and settings.anthropic_api_key:
            return _generate_anthropic(system_prompt, user_prompt)

        logger.warning(
            f"No API key configured for LLM provider '{provider}'; using grounded fallback."
        )
        return _fallback_response(user_prompt)

    except Exception as exc:  # noqa: BLE001 - we want to always return *something*
        logger.error(f"LLM generation failed ({provider}): {exc}")
        return _fallback_response(user_prompt)
