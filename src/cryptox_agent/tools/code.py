from __future__ import annotations

from dataclasses import dataclass
import subprocess
import tempfile
from pathlib import Path


@dataclass
class CodeInterpreter:
    timeout_seconds: int = 20

    def run_python(self, code: str) -> str:
        with tempfile.TemporaryDirectory(prefix="codexx-code-") as tmp:
            script = Path(tmp) / "snippet.py"
            script.write_text(code, encoding="utf-8")
            result = subprocess.run(
                ["python", str(script)],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        return self._format_result(result)

    def run_command(self, command: list[str], cwd: str | None = None) -> str:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        return self._format_result(result)

    @staticmethod
    def _format_result(result: subprocess.CompletedProcess[str]) -> str:
        return (
            f"exit_code={result.returncode}\n"
            f"stdout:\n{result.stdout.strip()}\n\n"
            f"stderr:\n{result.stderr.strip()}"
        )
