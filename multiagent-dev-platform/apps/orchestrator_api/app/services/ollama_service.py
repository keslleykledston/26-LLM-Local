"""
Ollama Service - Local LLM integration
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from loguru import logger

from app.core.config import settings


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0):
    """Decorator for retrying async functions with exponential backoff"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                        raise last_exception
                except Exception as e:
                    # Don't retry on other exceptions (e.g., validation errors)
                    logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                    raise

            raise last_exception

        return wrapper
    return decorator


class OllamaService:
    """Service for interacting with local Ollama LLM"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text completion using Ollama

        Args:
            prompt: The prompt to send to the model
            model: Model to use (defaults to configured model)
            system: System message for the model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            model_name = model or self.model

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            if system:
                payload["system"] = system

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")

        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Chat completion using Ollama

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response
        """
        try:
            model_name = model or self.model

            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")

        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings using Ollama

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            List of embedding values
        """
        try:
            model_name = model or self.embedding_model

            payload = {
                "model": model_name,
                "prompt": text,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding", [])

        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return data.get("models", [])

        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            raise

    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            payload = {"name": model, "stream": False}

            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json=payload,
                )
                response.raise_for_status()
                return True

        except Exception as e:
            logger.error(f"Failed to pull model {model}: {e}")
            return False
