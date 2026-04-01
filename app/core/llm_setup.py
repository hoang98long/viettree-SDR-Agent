# app/core/llm_setup.py
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from app.core.config import settings

# Heavy reasoning model for copywriting and QA
premium_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=settings.OPENAI_API_KEY
)

# Lightweight local model for data extraction and basic processing
extraction_llm = ChatOllama(
    model="llama3",
    temperature=0,
    base_url=settings.OLLAMA_BASE_URL,
    format="json"
)