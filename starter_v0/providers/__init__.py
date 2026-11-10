from providers.openai_provider import OpenAIProvider


def make_provider(name: str):
    if name == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unsupported provider: {name}. This project uses OpenAI only.")
