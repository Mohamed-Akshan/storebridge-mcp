from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from core.config import settings


def get_model(provider):
    if provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            timeout=18,
            max_retries=0,
            reasoning_effort="none",
        )

    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        timeout=18,
        max_retries=0,
    )


async def invoke_with_fallback(messages, tools=None, config=None):
    errors = []

    for provider in ("openai", "gemini"):
        try:
            model = get_model(provider)

            if tools:
                model = model.bind_tools(tools)

            return await model.ainvoke(messages, config=config)

        except Exception as error:
            errors.append(f"{provider}: {type(error).__name__}")

    raise RuntimeError("Both model providers are unavailable: " + ", ".join(errors))
