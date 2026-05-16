from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import json
import smtplib
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cryptox_agent.config import Settings


@dataclass
class TelegramClient:
    token: str
    chat_id: str

    def send_message(self, text: str) -> str:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = urlencode({"chat_id": self.chat_id, "text": text[:4000]}).encode()
        request = Request(url, data=data, method="POST")
        with urlopen(request, timeout=15) as response:  # nosec: explicit Telegram integration
            return response.read().decode("utf-8", errors="ignore")


@dataclass
class EmailClient:
    settings: Settings

    def send(self, subject: str, body: str, to_email: str | None = None) -> None:
        if not self.settings.smtp_host or not self.settings.smtp_user or not self.settings.smtp_password:
            raise ValueError("SMTP settings are incomplete")
        recipient = to_email or self.settings.report_email_to
        if not recipient:
            raise ValueError("No report email recipient configured")

        message = EmailMessage()
        message["From"] = self.settings.smtp_user
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self.settings.smtp_user, self.settings.smtp_password)
            smtp.send_message(message)


def call_json_api(url: str, payload: dict | None = None, method: str = "GET") -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=20) as response:  # nosec: explicit API integration
        raw = response.read().decode("utf-8", errors="ignore")
    return json.loads(raw)
