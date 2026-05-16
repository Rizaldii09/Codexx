from cryptox_agent.scheduler import Job, WorkflowScheduler


class DummyAgent:
    def __init__(self):
        self.sent = []

    def research(self, topic):
        return f"report:{topic}"

    def send_report(self, report, telegram=False, email=False):
        self.sent.append((report, telegram, email))


def test_scheduler_runs_due_job():
    agent = DummyAgent()
    scheduler = WorkflowScheduler(agent, [Job("j1", "research", "airdrop", 0, telegram=True)])

    executed = scheduler.run_pending_once()

    assert executed == ["j1"]
    assert agent.sent == [("report:airdrop", True, False)]
