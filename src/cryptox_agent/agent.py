from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from cryptox_agent.config import Settings
from cryptox_agent.prompts import DEFAULT_SYSTEM_PROMPT, RESEARCH_PROMPT
from cryptox_agent.llm import LLMRequest, build_llm_provider
from cryptox_agent.rag import KnowledgeBase
from cryptox_agent.tools.code import CodeInterpreter
from cryptox_agent.tools.messaging import EmailClient, TelegramClient
from cryptox_agent.tools.web import WebTools


@dataclass
class CryptoAgent:
    settings: Settings = field(default_factory=Settings.from_env)
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    web: WebTools = field(default_factory=WebTools)
    code: CodeInterpreter = field(default_factory=CodeInterpreter)

    def chat(self, message: str, context: str = "") -> str:
        provider = build_llm_provider(self.settings)
        if provider is None:
            return self._local_response(message, context)
        return provider.generate(LLMRequest(self.system_prompt, message, context))

    def research(self, topic: str, use_web: bool = True) -> str:
        evidence = ""
        if use_web:
            queries = [
                f"{topic} crypto airdrop early project",
                f"{topic} NFT mint early whitelist",
                f"{topic} crypto narrative Twitter X",
            ]
            snapshots = []
            for query in queries:
                try:
                    snapshots.append(f"QUERY: {query}\n{self.web.search_snapshot(query, max_chars=2500)}")
                except Exception as exc:  # noqa: BLE001 - report partial tool failure to agent/user
                    snapshots.append(f"QUERY: {query}\nWEB_ERROR: {exc}")
            evidence = "\n\n".join(snapshots)
        return self.chat(RESEARCH_PROMPT.format(topic=topic), context=evidence)

    def ask_kb(self, question: str) -> str:
        kb = KnowledgeBase(self.settings.rag_db_path)
        hits = kb.search(question)
        context = "\n".join(f"SOURCE: {path}\n{snippet}" for path, snippet in hits)
        return self.chat(question, context=context)

    def send_report(self, report: str, telegram: bool = False, email: bool = False) -> None:
        if telegram:
            if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
                raise ValueError("Telegram settings are incomplete")
            TelegramClient(self.settings.telegram_bot_token, self.settings.telegram_chat_id).send_message(report)
        if email:
            EmailClient(self.settings).send("Codexx Crypto Agent Report", report)

    def coding_plan(self, task: str, repo_path: str = ".") -> str:
        repo = Path(repo_path).resolve()
        file_overview = "\n".join(str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts)
        prompt = (
            f"Buat rencana autonomous coding/research untuk task ini: {task}\n"
            "Tahap wajib: planning, browsing/searching bila perlu, edit file, run test, dan draft PR.\n"
            f"Repo files:\n{file_overview[:8000]}"
        )
        return self.chat(prompt)

    def _local_response(self, message: str, context: str = "") -> str:
        return (
            "Mode lokal aktif karena AI_PROVIDER=local atau belum ada provider LLM yang dikonfigurasi.\n\n"
            f"Prompt sistem:\n{self.system_prompt}\n\n"
            f"Konteks:\n{context[:3000] if context else '-'}\n\n"
            f"Permintaan:\n{message}\n\n"
            "Next step: set AI_PROVIDER dan API key provider (Claude/DeepSeek/GLM) agar agent bisa membuat analisis generatif penuh."
        )
