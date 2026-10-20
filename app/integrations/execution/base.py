from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionOutput:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    duration_ms: int


class ExecutionUnavailable(Exception):
    """The executor can't run this language (or isn't configured)."""


class CodeExecutor(ABC):
    name: str

    @abstractmethod
    def supports(self, language: str) -> bool: ...

    @abstractmethod
    async def execute(
        self,
        language: str,
        source: str,
        *,
        files: dict[str, str] | None = None,
        entry: str | None = None,
        timeout_seconds: float | None = None,
    ) -> ExecutionOutput:
        """Runs `source` as the program. `files` are written next to it (e.g. a solution and its tests);
        `entry` names the program file when the default (main.py, main.js) won't do; `timeout_seconds`
        overrides the executor's default limit (whole test suites need longer than a single run)."""


class DisabledExecutor(CodeExecutor):
    name = "disabled"

    def supports(self, language: str) -> bool:
        return False

    async def execute(
        self,
        language: str,
        source: str,
        *,
        files: dict[str, str] | None = None,
        entry: str | None = None,
        timeout_seconds: float | None = None,
    ) -> ExecutionOutput:
        raise ExecutionUnavailable("Code execution is turned off on this server.")
