from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from urllib.request import Request, urlopen

from cryptox_agent.config import Settings


class LLMError(RuntimeError):
    """Raised when a configured LLM provider cannot return a response."""


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str
    message: str
    context: str = ""

    @property
    def user_content(self) -> str:
        if not self.context:
            return self.message
        return f"KONTEKS TOOL/RAG:\n{self.context}\n\nUSER:\n{self.message}"


class BaseLLMProvider:
    def generate(self, request: LLMRequest) -> str:
        raise NotImplementedError


@dataclass
class AnthropicProvider(BaseLLMProvider):
    api_key: str
    model: str
    base_url: str = "https://api.anthropic.com/v1"
    timeout: int = 60
    max_tokens: int = 4096
    api_version: str = "2023-06-01"

    def generate(self, request: LLMRequest) -> str:
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": request.system_prompt,
            "messages": [{"role": "user", "content": request.user_content}],
        }
        response = _post_json(
            f"{self.base_url.rstrip('/')}/messages",
            payload,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json",
            },
            timeout=self.timeout,
        )
        parts = [item.get("text", "") for item in response.get("content", []) if item.get("type") == "text"]
        text = "".join(parts).strip()
        if not text:
            raise LLMError(f"Anthropic response did not contain text: {response}")
        return text


@dataclass
class OpenAICompatibleProvider(BaseLLMProvider):
    api_key: str
    model: str
    base_url: str
    timeout: int = 60
    max_tokens: int = 4096

    def generate(self, request: LLMRequest) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_content},
            ],
            "max_tokens": self.max_tokens,
        }
        response = _post_json(
            f"{self.base_url.rstrip('/')}/chat/completions",
            payload,
            headers={
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json",
            },
            timeout=self.timeout,
        )
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"OpenAI-compatible response did not contain chat content: {response}") from exc
        if not content:
            raise LLMError(f"OpenAI-compatible response content was empty: {response}")
        return str(content).strip()


def build_llm_provider(settings: Settings) -> BaseLLMProvider | None:
    provider = settings.ai_provider.lower()
    if provider in {"local", "none", "mock"}:
        return None
    if provider in {"anthropic", "claude"}:
        if not settings.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY is required for AI_PROVIDER=anthropic")
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.ai_model,
            base_url=settings.anthropic_base_url,
            max_tokens=settings.llm_max_tokens,
        )
    if provider in {"deepseek", "glm", "zai", "zhipu", "openai-compatible", "compatible"}:
        api_key = _compatible_key(settings, provider)
        if not api_key:
            raise LLMError(f"API key is required for AI_PROVIDER={settings.ai_provider}")
        return OpenAICompatibleProvider(
            api_key=api_key,
            model=settings.ai_model,
            base_url=_compatible_base_url(settings, provider),
            max_tokens=settings.llm_max_tokens,
        )
    raise LLMError(f"Unsupported AI_PROVIDER={settings.ai_provider}. Use anthropic, deepseek, glm, openai-compatible, or local.")


def _compatible_key(settings: Settings, provider: str) -> str | None:
    if provider == "deepseek":
        return settings.deepseek_api_key or settings.compatible_api_key
    if provider in {"glm", "zai", "zhipu"}:
        return settings.glm_api_key or settings.compatible_api_key
    return settings.compatible_api_key or settings.deepseek_api_key or settings.glm_api_key


def _compatible_base_url(settings: Settings, provider: str) -> str:
    if settings.compatible_base_url:
        return settings.compatible_base_url
    if provider == "deepseek":
        return settings.deepseek_base_url
    if provider in {"glm", "zai", "zhipu"}:
        return settings.glm_base_url
    return settings.deepseek_base_url


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers=headers, method="POST")
    with urlopen(request, timeout=timeout) as response:  # nosec: explicit provider API call
        raw = response.read().decode("utf-8", errors="ignore")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise LLMError(f"Provider returned non-object JSON: {parsed}")
    return parsed
