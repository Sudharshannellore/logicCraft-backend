"""Domain errors. Services raise these; the API layer turns them into JSON responses."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "bad_request"

    headers: dict[str, str] | None = None

    def __init__(self, message: str, *, details: dict[str, Any] | None = None, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        if code:
            self.code = code


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
    headers = {"WWW-Authenticate": "Bearer"}


class TooManyAttemptsError(AppError):
    status_code = 429
    code = "too_many_attempts"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class InsufficientXpError(AppError):
    status_code = 402
    code = "insufficient_xp"

    def __init__(self, needed: int, balance: int | None = None):
        super().__init__(
            f"Not enough XP: this costs {needed} XP.",
            details={"needed": needed, **({"balance": balance} if balance is not None else {})},
        )


class UnprocessableError(AppError):
    status_code = 422
    code = "unprocessable"


class ServiceUnavailableError(AppError):
    """An outside service we depend on (e.g. Exercism on GitHub) can't be reached."""

    status_code = 503
    code = "service_unavailable"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
            headers=exc.headers,
        )
