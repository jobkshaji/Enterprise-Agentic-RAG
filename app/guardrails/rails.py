import logfire
from pydantic import SecretStr
from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.integrations.langchain.llm_adapter import LangChainLLMAdapter

from app.config import settings
from app.guardrails.colang_rules import COLANG_CONTENT, YAML_CONTENT, RAIL_INDICATORS


_rails: LLMRails | None = None

# Maps NeMo token → user-friendly message returned to the frontend.
_FRIENDLY_RESPONSES: dict[str, str] = {
    "JAILBREAK_BLOCKED": (
        "I maintain consistent guidelines regardless of how I am prompted. "
        "I am here to help with Kubernetes, Intel, and networking. "
        "What can I help you with?"
    ),
    "OFF_TOPIC_BLOCKED": (
        "I'm an Enterprise IT Assistant focused on Kubernetes, Intel hardware, "
        "and networking. I can't help with that — but ask me anything technical!"
    ),
    "GREETING_HANDLED": (
        "Hello! I'm your Enterprise IT Assistant. I specialise in Kubernetes, "
        "Intel hardware, and enterprise networking. "
        "What can I help you with today?"
    ),
    "CAPABILITIES_HANDLED": (
        "I'm an Enterprise AI Assistant with deep expertise in: "
        "Kubernetes (deployment, scaling, networking, operators), "
        "Intel Hardware (CPUs, FPGAs, SRIOV, NICs), "
        "Enterprise Networking (SDN, VLANs, BGP, routing). "
        "Ask me anything in these areas!"
    ),
    "FAREWELL_HANDLED": (
        "Goodbye! Feel free to return whenever you have more "
        "enterprise IT questions. Have a great day!"
    ),
}


def initialize_rails() -> None:
    """
    Build the NeMo LLMRails singleton at app startup.
    Uses openai/gpt-oss-20b via Groq for fast intent classification at
    the gate — the heavier model is reserved for the RAG pipeline.
    """
    global _rails

    guard_llm = ChatGroq(
        api_key=SecretStr(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None,
        model="openai/gpt-oss-120b",
        temperature=0,
        reasoning_format="hidden",
    )

    config = RailsConfig.from_content(
        colang_content=COLANG_CONTENT,
        yaml_content=YAML_CONTENT
    )

    _rails = LLMRails(config, llm=LangChainLLMAdapter(guard_llm))
    logfire.info("🛡️ NeMo Guardrails initialised (openai/gpt-oss-20b).")


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through the NeMo rails gate.

    Returns:
        (True,  rail_response) — a rail fired; return the friendly message
                                 immediately, skip the RAG pipeline.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    if _rails is None:
        logfire.warning("⚠️ Guardrails not initialised — skipping gate.")
        return False, None

    with logfire.span("🛡️ Guardrails Check"):
        result = _rails.generate(messages=[{"role": "user", "content": message}])

        # NeMo returns {'role': 'assistant', 'content': '...'} — extract text
        content = result.get("content", "") if isinstance(result, dict) else str(result)
        content = content.strip()

        logfire.info(f"🛡️ NeMo raw response: '{content[:200]}'")

        # Check if any rail token appears in the NeMo response
        for indicator in RAIL_INDICATORS:
            if indicator in content:
                friendly = _FRIENDLY_RESPONSES.get(indicator, content)
                logfire.info(
                    f"🛡️ Rail fired: {indicator} | query='{message[:80]}'"
                )
                return True, friendly

        logfire.info("✅ Guardrails passed.")
        return False, None