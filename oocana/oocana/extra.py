from typing import Literal, TypedDict

__all__ = ["LLMModelOptions", "LLMMessage"]

class LLMModelOptions(TypedDict):
    model: str
    temperature: float
    top_p: float
    max_tokens: int

class LLMMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str
