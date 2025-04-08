from langchain_openai import AzureChatOpenAI, ChatOpenAI
from .config import Settings

def get_llm(settings: Settings):
    """
    Get the LLM provider based on the configuration.
    """
    provider = settings.LLM_PROVIDER.lower()
    temperature = settings.OPENAI_TEMPERATURE
    if provider == "azure":
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=temperature,
        )

    if provider == "openai":
        return ChatOpenAI(
            model_name=settings.OPENAI_API_VERSION,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_ENDPOINT,
            temperature=temperature,
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")
