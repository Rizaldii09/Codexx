from cryptox_agent.config import Settings


def test_settings_loads_dotenv_file(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("AI_MODEL", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AI_PROVIDER=deepseek\nAI_MODEL=deepseek-chat\nDEEPSEEK_API_KEY=from-dotenv\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)

    assert settings.ai_provider == "deepseek"
    assert settings.ai_model == "deepseek-chat"
    assert settings.deepseek_api_key == "from-dotenv"


def test_real_environment_overrides_dotenv_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("AI_PROVIDER=deepseek\nDEEPSEEK_API_KEY=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("AI_PROVIDER", "glm")
    monkeypatch.setenv("GLM_API_KEY", "from-shell")

    settings = Settings.from_env(env_file)

    assert settings.ai_provider == "glm"
    assert settings.glm_api_key == "from-shell"


def test_settings_finds_dotenv_in_parent_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("AI_PROVIDER=anthropic\nANTHROPIC_API_KEY=parent-key\n", encoding="utf-8")
    child = tmp_path / "nested" / "folder"
    child.mkdir(parents=True)
    monkeypatch.chdir(child)

    settings = Settings.from_env()

    assert settings.ai_provider == "anthropic"
    assert settings.anthropic_api_key == "parent-key"
