from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from ipl_agent.config import Config, ModelConfig, ModelProvider


def create_llm(model_config: ModelConfig) -> BaseChatModel:
    if model_config.provider == ModelProvider.OLLAMA:
        return ChatOllama(
            model=model_config.name,
            temperature=model_config.temperature,
            num_ctx=Config.OLLAMA_CONTEXT_WINDOW,
            verbose=False,
            keep_alive=-1
        )
    elif model_config.provider == ModelProvider.GOOGLE:
        return ChatGoogleGenerativeAI(
            model=model_config.name,
            temperature=model_config.temperature,
            max_retries=1
        )
    elif model_config.provider == ModelProvider.GROQ:
        return ChatGroq(
            model=model_config.name,
            temperature=model_config.temperature
        )
    