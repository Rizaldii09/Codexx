from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from cryptox_agent.tools.files import iter_text_files, read_text_file


@dataclass
class KnowledgeBase:
    db_path: str

    def connect(self) -> sqlite3.Connection:
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(path, content, tokenize='porter')"
        )
        return connection

    def add_document(self, path: str, content: str) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM docs WHERE path = ?", (path,))
            connection.execute("INSERT INTO docs(path, content) VALUES (?, ?)", (path, content))

    def ingest_paths(self, paths: list[str]) -> int:
        count = 0
        for file_path in iter_text_files(paths):
            self.add_document(str(file_path), read_text_file(file_path, max_chars=200000))
            count += 1
        return count

    def search(self, query: str, limit: int = 5) -> list[tuple[str, str]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT path, snippet(docs, 1, '[', ']', '...', 18) FROM docs WHERE docs MATCH ? LIMIT ?",
                (query, limit),
            ).fetchall()
        return [(row[0], row[1]) for row in rows]
