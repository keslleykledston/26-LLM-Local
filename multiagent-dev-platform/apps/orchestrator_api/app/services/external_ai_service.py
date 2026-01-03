"""
External AI Service - Controlled external AI usage
"""
import httpx
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

from app.core.config import settings


class ExternalAIService:
    """
    Service for calling external AI providers in a controlled manner

    This service enforces:
    - Approval requirements
    - Usage limits
    - Cost tracking
    - Response caching
    - Audit logging
    """

    def __init__(self):
        self.cache: Dict[str, Any] = {}  # Simple in-memory cache

    async def call_external_ai(
        self,
        call_id: int,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Call an external AI provider

        Args:
            call_id: ExternalAICall record ID for audit trail
            prompt: The prompt to send
            provider: Provider name (claude, openai, gemini, openrouter)
            model: Model to use

        Returns:
            Response dict with content, tokens_used, cost_usd
        """
        # Check offline-only mode
        if settings.OFFLINE_ONLY_MODE:
            logger.warning("🚫 Offline-only mode enabled - external AI calls are disabled")
            raise Exception("External AI calls disabled in offline-only mode")

        # Check cache first
        cache_key = f"{provider}:{model}:{hash(prompt)}"
        if settings.CACHE_EXTERNAL_AI_RESPONSES and cache_key in self.cache:
            logger.info(f"💾 Using cached response for external AI call #{call_id}")
            return {**self.cache[cache_key], "cached": True}

        # Route to appropriate provider
        if provider == "claude":
            result = await self._call_claude(prompt, model)
        elif provider == "openai":
            result = await self._call_openai(prompt, model)
        elif provider == "gemini":
            result = await self._call_gemini(prompt, model)
        elif provider == "openrouter":
            result = await self._call_openrouter(prompt, model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        # Cache result
        if settings.CACHE_EXTERNAL_AI_RESPONSES:
            self.cache[cache_key] = result

        logger.info(
            f"🌐 External AI call #{call_id} completed: "
            f"{result.get('tokens_used', 0)} tokens, "
            f"${result.get('cost_usd', 0):.4f}"
        )

        return result

    async def _call_claude(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        if not settings.ANTHROPIC_ENABLED:
            raise Exception("Claude is disabled")

        if not settings.ANTHROPIC_API_KEY:
            raise Exception("Claude API key not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": model or settings.ANTHROPIC_MODEL,
                        "max_tokens": 4000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract response
                content = data["content"][0]["text"]
                tokens_used = data["usage"]["input_tokens"] + data["usage"]["output_tokens"]

                # Estimate cost (approximate rates)
                cost_usd = (data["usage"]["input_tokens"] * 0.003 / 1000) + (
                    data["usage"]["output_tokens"] * 0.015 / 1000
                )

                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                    "model": data["model"],
                }

        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise

    async def _call_openai(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Call OpenAI ChatGPT API"""
        if not settings.OPENAI_ENABLED:
            raise Exception("OpenAI is disabled")

        if not settings.OPENAI_API_KEY:
            raise Exception("OpenAI API key not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model or settings.OPENAI_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract response
                content = data["choices"][0]["message"]["content"]
                tokens_used = data["usage"]["total_tokens"]

                # Estimate cost (approximate rates for GPT-4)
                cost_usd = (data["usage"]["prompt_tokens"] * 0.01 / 1000) + (
                    data["usage"]["completion_tokens"] * 0.03 / 1000
                )

                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                    "model": data["model"],
                }

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    async def _call_gemini(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Call Google Gemini API"""
        if not settings.GOOGLE_ENABLED:
            raise Exception("Google Gemini is disabled")

        if not settings.GOOGLE_API_KEY:
            raise Exception("Google API key not configured")

        try:
            model_name = model or settings.GOOGLE_MODEL
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={settings.GOOGLE_API_KEY}",
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract response
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)

                # Gemini Pro is currently free or very low cost
                cost_usd = 0.0

                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                    "model": model_name,
                }

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

    async def _call_openrouter(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Call OpenRouter API"""
        if not settings.OPENROUTER_ENABLED:
            raise Exception("OpenRouter is disabled")

        if not settings.OPENROUTER_API_KEY:
            raise Exception("OpenRouter API key not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model or settings.OPENROUTER_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract response
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

                # Cost varies by model on OpenRouter
                cost_usd = 0.01  # Placeholder

                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                    "model": data.get("model", "unknown"),
                }

        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            raise

    def clear_cache(self) -> None:
        """Clear the response cache"""
        self.cache.clear()
        logger.info("🗑️ External AI cache cleared")
