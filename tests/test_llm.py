import json

import cryptox_agent.llm as llm
from cryptox_agent.config import Settings
from cryptox_agent.llm import LLMRequest, build_llm_provider


def test_builds_anthropic_provider():
    provider = build_llm_provider(
        Settings(ai_provider="claude", ai_model="claude-test", anthropic_api_key="key")
    )

    assert provider.model == "claude-test"


def test_builds_deepseek_provider():
    provider = build_llm_provider(
        Settings(ai_provider="deepseek", ai_model="deepseek-chat", deepseek_api_key="key")
    )

    assert provider.base_url == "https://api.deepseek.com/v1"


def test_builds_glm_provider():
    provider = build_llm_provider(Settings(ai_provider="glm", ai_model="glm-4-flash", glm_api_key="key"))

    assert provider.base_url == "https://open.bigmodel.cn/api/paas/v4"


def test_anthropic_provider_parses_text(monkeypatch):
    captured = {}

    def fake_post_json(url, payload, headers, timeout):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout})
        return {"content": [{"type": "text", "text": "jawaban claude"}]}

    monkeypatch.setattr(llm, "_post_json", fake_post_json)
    provider = llm.AnthropicProvider("key", "claude-test")

    result = provider.generate(LLMRequest("system", "hello", "ctx"))

    assert result == "jawaban claude"
    assert captured["url"].endswith("/messages")
    assert captured["headers"]["x-api-key"] == "key"
    assert captured["payload"]["system"] == "system"
    assert "KONTEKS TOOL/RAG" in captured["payload"]["messages"][0]["content"]


def test_openai_compatible_provider_parses_chat_content(monkeypatch):
    captured = {}

    def fake_post_json(url, payload, headers, timeout):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout})
        return {"choices": [{"message": {"content": "jawaban compatible"}}]}

    monkeypatch.setattr(llm, "_post_json", fake_post_json)
    provider = llm.OpenAICompatibleProvider("key", "deepseek-chat", "https://api.deepseek.com/v1")

    result = provider.generate(LLMRequest("system", "hello"))

    assert result == "jawaban compatible"
    assert captured["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert captured["headers"]["authorization"] == "Bearer key"
    assert captured["payload"]["messages"][0] == {"role": "system", "content": "system"}


def test_post_json_rejects_non_object(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(["not", "object"]).encode()

    monkeypatch.setattr(llm, "urlopen", lambda request, timeout: FakeResponse())

    try:
        llm._post_json("https://example.test", {}, {}, 1)
    except llm.LLMError as exc:
        assert "non-object" in str(exc)
    else:
        raise AssertionError("Expected LLMError")
