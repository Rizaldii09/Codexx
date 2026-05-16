from __future__ import annotations

from pathlib import Path

TEXT_SUFFIXES = {".txt", ".md", ".mdx", ".py", ".js", ".ts", ".tsx", ".json", ".yaml", ".yml", ".html", ".css"}


def read_text_file(path: str | Path, max_chars: int = 10000) -> str:
    file_path = Path(path).expanduser().resolve()
    return file_path.read_text(encoding="utf-8", errors="ignore")[:max_chars]


def iter_text_files(paths: list[str | Path]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                    files.append(child)
    return files
