from app.core.config import Settings
from app.integrations.execution.base import CodeExecutor, DisabledExecutor, ExecutionOutput
from app.integrations.execution.local import LocalExecutor


def build_executor(settings: Settings) -> CodeExecutor:
    if settings.code_executor == "local":
        return LocalExecutor(
            timeout_seconds=settings.code_timeout_seconds,
            memory_limit_mb=settings.code_memory_limit_mb,
            max_output_bytes=settings.code_max_output_bytes,
            max_concurrent=settings.code_max_concurrent,
        )
    return DisabledExecutor()


__all__ = ["CodeExecutor", "ExecutionOutput", "build_executor"]
