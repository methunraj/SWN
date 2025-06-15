from .base import BaseProvider
from .ollama import OllamaProvider
from .llamacpp import LlamaCppProvider
from app.models import Provider
from typing import Dict, Type

PROVIDER_MAP: Dict[Provider, Type[BaseProvider]] = {
    Provider.OLLAMA: OllamaProvider,
    Provider.LLAMACPP: LlamaCppProvider
}

__all__ = ["BaseProvider", "OllamaProvider", "LlamaCppProvider", "PROVIDER_MAP"]