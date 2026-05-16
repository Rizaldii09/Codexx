from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._skip = tag in {"script", "style", "noscript"}

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)

    def text(self) -> str:
        return "\n".join(self.parts)


@dataclass
class WebTools:
    timeout: int = 15
    user_agent: str = "CodexxAgent/0.1 (+research bot)"

    def fetch_text(self, url: str, max_chars: int = 8000) -> str:
        request = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout) as response:  # nosec: user-controlled research tool
            html = response.read(max_chars * 4).decode("utf-8", errors="ignore")
        parser = TextExtractor()
        parser.feed(html)
        return parser.text()[:max_chars]

    def search_url(self, query: str) -> str:
        return f"https://duckduckgo.com/html/?q={quote_plus(query)}"

    def search_snapshot(self, query: str, max_chars: int = 6000) -> str:
        return self.fetch_text(self.search_url(query), max_chars=max_chars)
