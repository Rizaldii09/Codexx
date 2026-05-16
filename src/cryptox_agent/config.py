from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    ai_provider: str = "local"
    ai_model: str = "claude-3-5-sonnet-latest"
    anthropic_api_key: str | None = None
    anthropic_base_url: str = "https://api.anthropic.com/v1"
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    glm_api_key: str | None = None
    glm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    compatible_api_key: str | None = None
    compatible_base_url: str | None = None
    llm_max_tokens: int = 4096
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    report_email_to: str | None = None
    rag_db_path: str = ".codexx/rag.sqlite"

    @classmethod
    def from_env(cls) -> "Settings":
        provider = os.getenv("AI_PROVIDER", "local")
        return cls(
            ai_provider=provider,
            ai_model=os.getenv("AI_MODEL", _default_model(provider)),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
            anthropic_base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"),
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY") or None,
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            glm_api_key=os.getenv("GLM_API_KEY") or None,
            glm_base_url=os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            compatible_api_key=os.getenv("COMPATIBLE_API_KEY") or None,
            compatible_base_url=os.getenv("COMPATIBLE_BASE_URL") or None,
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
            smtp_host=os.getenv("SMTP_HOST") or None,
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER") or None,
            smtp_password=os.getenv("SMTP_PASSWORD") or None,
            report_email_to=os.getenv("REPORT_EMAIL_TO") or None,
            rag_db_path=os.getenv("RAG_DB_PATH", ".codexx/rag.sqlite"),
        )


def _default_model(provider: str) -> str:
    provider = provider.lower()
    if provider in {"anthropic", "claude"}:
        return "claude-3-5-sonnet-latest"
    if provider == "deepseek":
        return "deepseek-chat"
    if provider in {"glm", "zai", "zhipu"}:
        return "glm-4-flash"
    return "local"
