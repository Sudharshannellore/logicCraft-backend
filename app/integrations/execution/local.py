"""Runs learners' code on this server, in a locked-down child process.

Defence in depth, with no containers or external runner:

1. OS limits. On Windows a Job Object caps memory and CPU time and forbids child processes; on
   Linux/macOS rlimits do the same job. The whole process tree is killed on timeout.
2. Runtime guards (see harness.py). Python's audit hook denies files outside the standard
   library, subprocesses, sockets and ctypes; Node's permission model denies the filesystem, child
   processes and workers, and the guard removes network modules.
3. Hygiene. A throwaway working directory, an environment stripped of the API's secrets, output
   captured to size-capped files, low CPU priority, and a cap on concurrent runs.

This makes casual abuse (reading the server's files, phoning home, fork bombs, memory bombs,
infinite loops) fail. It is not a VM-grade boundary: also run the API as a low-privilege OS user.
"""

import asyncio
import contextlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app.integrations.execution.base import CodeExecutor, ExecutionOutput, ExecutionUnavailable

logger = logging.getLogger(__name__)

IS_WINDOWS = sys.platform == "win32"
_FILENAMES = {"python": "main.py", "javascript": "main.js", "typescript": "main.mjs"}
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]*$")
_NODE_FOOTER = re.compile(r"^Node\.js v\d")


def _python_interpreter() -> str:
    # A venv's python.exe on Windows is a launcher that starts the real interpreter as a *child*
    # process, which the one-process job limit forbids — so run the base interpreter directly.
    return getattr(sys, "_base_executable", None) or sys.executable


def _node_permission_flag(node: str) -> str | None:
    """`--permission` (Node 22.13+/23.5+), the older experimental flag, or None if unsupported."""
    for flag in ("--permission", "--experimental-permission"):
        try:
            probe = subprocess.run([node, flag, "-e", ""], capture_output=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if probe.returncode == 0:
            return flag
    return None


class LocalExecutor(CodeExecutor):
    name = "local"

    def __init__(
        self,
        *,
        timeout_seconds: float,
        memory_limit_mb: int = 256,
        max_output_bytes: int = 64_000,
        max_concurrent: int = 4,
    ):
        self.timeout_seconds = timeout_seconds
        self.memory_bytes = memory_limit_mb * 1024 * 1024
        self.max_output_bytes = max_output_bytes
        self._slots = asyncio.Semaphore(max_concurrent)
        self._python = _python_interpreter()
        self._node = shutil.which("node")
        self._node_flag = _node_permission_flag(self._node) if self._node else None
        if self._node and not self._node_flag:
            logger.warning("Node.js is too old for --permission (needs 20+); JavaScript execution is disabled.")
        if IS_WINDOWS:
            from app.integrations.execution.windows_job import WindowsJob  # noqa: F401 — fail fast if unavailable

    def supports(self, language: str) -> bool:
        return language == "python" or (language in ("javascript", "typescript") and self._node_flag is not None)

    def _command(self, language: str, script: Path) -> list[str]:
        if language == "python":
            # -I isolated (no env vars, no cwd on sys.path), -S no site-packages, -B no .pyc writes.
            return [self._python, "-I", "-S", "-B", "-X", "utf8", str(script)]
        heap_mb = max(32, self.memory_bytes * 3 // 4 // (1024 * 1024))
        # Reads only inside this run's own folder (the program, and the files written beside it).
        command = [self._node, self._node_flag, f"--allow-fs-read={script.parent}", f"--max-old-space-size={heap_mb}"]
        if language == "typescript":
            # Node 22.18+/23.6+ runs .ts directly; transform-types adds enums and namespaces.
            command += ["--experimental-transform-types", "--disable-warning=ExperimentalWarning"]
        return [*command, str(script)]

    def _environment(self, workdir: str) -> dict[str, str]:
        """Only what an interpreter needs to start — nothing from the API's own environment."""
        if IS_WINDOWS:
            return {
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"),
                "PATH": os.path.dirname(self._python),
                "TEMP": workdir,
                "TMP": workdir,
            }
        return {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": workdir, "TMPDIR": workdir, "LANG": "C.UTF-8"}

    def _read_capped(self, path: Path) -> str:
        with path.open("rb") as f:
            data = f.read(self.max_output_bytes + 1)
        text = data[: self.max_output_bytes].decode("utf-8", errors="replace")
        return text + "\n… output truncated" if len(data) > self.max_output_bytes else text

    def _spawn(
        self, command: list[str], workdir: str, stdout, stderr, timeout: float
    ) -> tuple[subprocess.Popen, object]:
        common = {
            "cwd": workdir,
            "env": self._environment(workdir),
            "stdin": subprocess.DEVNULL,
            "stdout": stdout,
            "stderr": stderr,
        }
        if IS_WINDOWS:
            from app.integrations.execution import windows_job as wj

            job = wj.WindowsJob(memory_bytes=self.memory_bytes, cpu_seconds=timeout + 1)
            flags = wj.CREATE_SUSPENDED | wj.BELOW_NORMAL_PRIORITY_CLASS | wj.CREATE_NO_WINDOW
            proc = subprocess.Popen(command, creationflags=flags, **common)
            try:
                job.adopt_and_resume(proc)
            except OSError:
                proc.kill()  # never let it run unconfined
                proc.wait()
                job.close()
                raise
            return proc, job

        import resource  # POSIX only

        cpu = int(timeout) + 1
        is_python = command[0] == self._python
        output_cap = self._output_cap

        def limit() -> None:  # runs in the child between fork and exec
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
            resource.setrlimit(resource.RLIMIT_FSIZE, (output_cap, output_cap))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
            if is_python:  # V8 reserves huge virtual ranges, so Node is capped by --max-old-space-size instead
                resource.setrlimit(resource.RLIMIT_AS, (self.memory_bytes, self.memory_bytes))
            os.nice(10)

        return subprocess.Popen(command, preexec_fn=limit, start_new_session=True, **common), None

    @staticmethod
    def _kill(proc: subprocess.Popen, job) -> None:
        if job is not None:
            job.terminate()
        else:
            import signal

            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGKILL)  # the whole session, not just the direct child
        proc.wait()

    @property
    def _output_cap(self) -> int:
        """Output kept on disk before the run is stopped (only the first `max_output_bytes` are returned)."""
        return self.max_output_bytes * 4

    def _wait(self, proc: subprocess.Popen, job, started: float, timeout: float, *outputs: Path) -> tuple[bool, bool]:
        """Waits for the run, killing it on timeout or an output flood. Returns (timed_out, flooded)."""
        deadline = started + timeout
        while True:
            try:
                proc.wait(timeout=0.05)
                return False, False
            except subprocess.TimeoutExpired:
                pass
            if time.perf_counter() >= deadline:
                self._kill(proc, job)
                return True, False
            if sum(p.stat().st_size for p in outputs) > self._output_cap:
                self._kill(proc, job)
                return False, True

    def _run(
        self, language: str, source: str, files: dict[str, str], entry: str | None, timeout: float
    ) -> ExecutionOutput:
        workdir = tempfile.mkdtemp(prefix="cq-run-")
        try:
            for name, content in files.items():
                if not _SAFE_NAME.match(name):  # flat folder only: no paths, no "..", no hidden files
                    raise ExecutionUnavailable(f"Refusing to write {name!r} into the run folder.")
                (Path(workdir) / name).write_text(content, encoding="utf-8")
            script = Path(workdir) / (entry or _FILENAMES[language])
            script.write_text(source, encoding="utf-8")
            out_path, err_path = Path(workdir) / "stdout.txt", Path(workdir) / "stderr.txt"
            with out_path.open("wb") as out, err_path.open("wb") as err:
                started = time.perf_counter()
                try:
                    proc, job = self._spawn(self._command(language, script), workdir, out, err, timeout)
                except OSError as exc:
                    raise ExecutionUnavailable(f"The code runner couldn't start: {exc}") from exc
                try:
                    timed_out, flooded = self._wait(proc, job, started, timeout, out_path, err_path)
                finally:
                    if job is not None:
                        job.close()
                duration = int((time.perf_counter() - started) * 1000)

            def clean(text: str) -> str:
                """Unix newlines, and no server paths in messages: `C:\\...\\cq-run-x\\main.js:3` becomes `main.js:3`."""
                text = text.replace("\r\n", "\n").replace(str(script), script.name)
                text = text.replace(Path(workdir).as_uri() + "/", "").replace(workdir + os.sep, "")
                # Node's own frames and version footer mean nothing to a learner.
                lines = [
                    line for line in text.split("\n") if "node:internal" not in line and not _NODE_FOOTER.match(line)
                ]
                return "\n".join(lines).strip("\n") + ("\n" if text.endswith("\n") else "")

            stderr = clean(self._read_capped(err_path))
            if timed_out:
                stderr = "Time limit exceeded"
            elif flooded or "file too large" in stderr.lower():  # our watchdog, or RLIMIT_FSIZE
                stderr = f"Your program printed too much output (over {self._output_cap // 1000} KB) and was stopped."
            elif "out of memory" in stderr.lower():
                stderr = f"Your program ran out of memory (the limit is {self.memory_bytes // (1024 * 1024)} MB)."
            elif proc.returncode != 0 and not stderr.strip():
                stderr = "Your program was stopped — it may have used too much memory or CPU."
            return ExecutionOutput(
                stdout=clean(self._read_capped(out_path)),
                stderr=stderr,
                exit_code=None if timed_out else proc.returncode,
                timed_out=timed_out,
                duration_ms=duration,
            )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    async def execute(
        self,
        language: str,
        source: str,
        *,
        files: dict[str, str] | None = None,
        entry: str | None = None,
        timeout_seconds: float | None = None,
    ) -> ExecutionOutput:
        if not self.supports(language):
            raise ExecutionUnavailable(f"Running {language} isn't available on this server yet.")
        if entry is not None and not _SAFE_NAME.match(entry):
            raise ExecutionUnavailable(f"Refusing to run {entry!r}.")
        async with self._slots:
            # A worker thread rather than asyncio subprocesses: those need the Proactor loop on Windows.
            timeout = timeout_seconds or self.timeout_seconds
            return await asyncio.to_thread(self._run, language, source, files or {}, entry, timeout)
