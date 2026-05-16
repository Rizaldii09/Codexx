from cryptox_agent.agent import CryptoAgent
from cryptox_agent.config import Settings


def test_local_chat_without_openai_key():
    agent = CryptoAgent(settings=Settings(ai_provider="local"))

    response = agent.chat("Apa kemampuanmu?")

    assert "Mode lokal aktif" in response
    assert "Apa kemampuanmu?" in response
    assert "Claude/DeepSeek/GLM" in response


def test_coding_plan_uses_repo_overview(tmp_path):
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    agent = CryptoAgent(settings=Settings(ai_provider="local"))

    response = agent.coding_plan("Tambah fitur", repo_path=str(tmp_path))

    assert "README.md" in response
    assert "planning" in response
