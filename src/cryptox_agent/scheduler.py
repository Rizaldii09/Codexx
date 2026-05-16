from __future__ import annotations

from dataclasses import dataclass
import json
import time
from pathlib import Path
from typing import Any

from cryptox_agent.agent import CryptoAgent


@dataclass
class Job:
    name: str
    kind: str
    topic: str
    interval_seconds: int
    telegram: bool = False
    email: bool = False
    last_run: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        return cls(
            name=data["name"],
            kind=data.get("kind", "research"),
            topic=data["topic"],
            interval_seconds=int(data.get("interval_seconds", 86400)),
            telegram=bool(data.get("telegram", False)),
            email=bool(data.get("email", False)),
        )


class WorkflowScheduler:
    def __init__(self, agent: CryptoAgent, jobs: list[Job]) -> None:
        self.agent = agent
        self.jobs = jobs

    @classmethod
    def from_json(cls, path: str, agent: CryptoAgent | None = None) -> "WorkflowScheduler":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        jobs = [Job.from_dict(item) for item in payload.get("jobs", [])]
        return cls(agent or CryptoAgent(), jobs)

    def run_pending_once(self) -> list[str]:
        now = time.time()
        executed: list[str] = []
        for job in self.jobs:
            if now - job.last_run < job.interval_seconds:
                continue
            if job.kind != "research":
                raise ValueError(f"Unsupported job kind: {job.kind}")
            report = self.agent.research(job.topic)
            self.agent.send_report(report, telegram=job.telegram, email=job.email)
            job.last_run = now
            executed.append(job.name)
        return executed

    def forever(self, poll_seconds: int = 30) -> None:
        while True:
            self.run_pending_once()
            time.sleep(poll_seconds)
