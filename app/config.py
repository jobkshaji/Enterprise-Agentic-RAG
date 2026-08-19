import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
    QDRANT_URL=os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_COLLECTION="enterprise_rag"
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    GROQ_FALLBACK_API_KEY=os.getenv("GROQ_FALLBACK_API_KEY")
    GROQ_MODEL="openai/gpt-oss-20b"

    # --- LLM GATEWAY (PORTKEY) ---
    PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
    PORTKEY_CONFIG_SLUG = "pc-rag-ai-805384"
    GROQ_SLUG = "groq"     # primary: @groq/openai/gpt-oss-20b
    GROQ_SLUG_2 = "brag"  # fallback: @brag/openai/gpt-oss-20b




settings=Settings()
