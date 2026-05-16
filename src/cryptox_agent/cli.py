from __future__ import annotations

import argparse

from cryptox_agent.agent import CryptoAgent
from cryptox_agent.config import Settings
from cryptox_agent.rag import KnowledgeBase
from cryptox_agent.scheduler import WorkflowScheduler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codexx Crypto AI Agent")
    parser.add_argument("--env-file", default=".env", help="Path to .env file; defaults to searching for .env from the current directory upward")
    sub = parser.add_subparsers(dest="command", required=True)

    chat = sub.add_parser("chat", help="Interactive-ish single prompt chat")
    chat.add_argument("message", nargs="?", default="Halo, jelaskan kemampuanmu")
    chat.add_argument("--prompt", default=None, help="Custom system prompt")

    research = sub.add_parser("research", help="Run one crypto/NFT/airdrop research report")
    research.add_argument("--topic", required=True)
    research.add_argument("--telegram", action="store_true")
    research.add_argument("--email", action="store_true")
    research.add_argument("--no-web", action="store_true")

    ingest = sub.add_parser("ingest", help="Ingest files/folders into the RAG knowledge base")
    ingest.add_argument("paths", nargs="+")

    ask_kb = sub.add_parser("ask-kb", help="Ask question using RAG context")
    ask_kb.add_argument("question")

    schedule = sub.add_parser("schedule", help="Run workflow scheduler forever")
    schedule.add_argument("--config", required=True)
    schedule.add_argument("--poll-seconds", type=int, default=30)

    coding = sub.add_parser("coding-plan", help="Create autonomous coding/research plan")
    coding.add_argument("task")
    coding.add_argument("--repo", default=".")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env(args.env_file)
    agent = CryptoAgent(settings=settings, system_prompt=args.prompt) if getattr(args, "prompt", None) else CryptoAgent(settings=settings)

    if args.command == "chat":
        print(agent.chat(args.message))
    elif args.command == "research":
        report = agent.research(args.topic, use_web=not args.no_web)
        print(report)
        agent.send_report(report, telegram=args.telegram, email=args.email)
    elif args.command == "ingest":
        count = KnowledgeBase(settings.rag_db_path).ingest_paths(args.paths)
        print(f"Ingested {count} files into {settings.rag_db_path}")
    elif args.command == "ask-kb":
        print(agent.ask_kb(args.question))
    elif args.command == "schedule":
        WorkflowScheduler.from_json(args.config, agent=agent).forever(poll_seconds=args.poll_seconds)
    elif args.command == "coding-plan":
        print(agent.coding_plan(args.task, repo_path=args.repo))
