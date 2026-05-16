from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shlex


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
    def from_env(cls, env_file: str | Path | None = ".env") -> "Settings":
        env = _merged_env(env_file)
        provider = env.get("AI_PROVIDER", "local")
        return cls(
            ai_provider=provider,
            ai_model=env.get("AI_MODEL", _default_model(provider)),
            anthropic_api_key=env.get("ANTHROPIC_API_KEY") or None,
            anthropic_base_url=env.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"),
            deepseek_api_key=env.get("DEEPSEEK_API_KEY") or None,
            deepseek_base_url=env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            glm_api_key=env.get("GLM_API_KEY") or None,
            glm_base_url=env.get("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            compatible_api_key=env.get("COMPATIBLE_API_KEY") or None,
            compatible_base_url=env.get("COMPATIBLE_BASE_URL") or None,
            llm_max_tokens=int(env.get("LLM_MAX_TOKENS", "4096")),
            telegram_bot_token=env.get("TELEGRAM_BOT_TOKEN") or None,
            telegram_chat_id=env.get("TELEGRAM_CHAT_ID") or None,
            smtp_host=env.get("SMTP_HOST") or None,
            smtp_port=int(env.get("SMTP_PORT", "587")),
            smtp_user=env.get("SMTP_USER") or None,
            smtp_password=env.get("SMTP_PASSWORD") or None,
            report_email_to=env.get("REPORT_EMAIL_TO") or None,
            rag_db_path=env.get("RAG_DB_PATH", ".codexx/rag.sqlite"),
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


def _merged_env(env_file: str | Path | None) -> dict[str, str]:
    dotenv_values = _load_env_file(env_file) if env_file else {}
    return {**dotenv_values, **os.environ}


def _load_env_file(env_file: str | Path) -> dict[str, str]:
    path = _resolve_env_file(env_file)
    if path is None:
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(raw_line)
        if parsed is not None:
            key, value = parsed
            values[key] = value
    return values


def _resolve_env_file(env_file: str | Path) -> Path | None:
    path = Path(env_file).expanduser()
    if path.is_absolute():
        return path if path.is_file() else None

    cwd = Path.cwd()
    for directory in (cwd, *cwd.parents):
        candidate = directory / path
        if candidate.is_file():
            return candidate
    return None


def _parse_env_line(raw_line: str) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()

    try:
        tokens = shlex.split(line, comments=True, posix=True)
    except ValueError:
        return None
    if not tokens:
        return None

    assignment = tokens[0]
    if "=" not in assignment:
        return None
    key, value = assignment.split("=", 1)
    key = key.strip()
    if not key:
        return None
    return key, value
