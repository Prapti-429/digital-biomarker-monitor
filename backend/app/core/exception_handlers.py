"""
Security Exception Handlers Module.

Maps domain-level authentication, authorization, and cryptographic exceptions
to standardized HTTP response payloads (RFC 7807 compliant).
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AccountDisabledException,
    AccountLockedException,
    AuthBaseException,
    DuplicateEntityError,
    EntityNotFoundError,
    InsufficientPermissionError,
    InvalidCredentialsException,
    InvalidTokenError,
    PasswordComplexityException,
    TokenExpiredError,
    TokenRevokedError,
)


def register_security_exception_handlers(app: FastAPI) -> None:
    """Registers exception handlers on the provided FastAPI application instance."""

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message, "code": "INVALID_CREDENTIALS"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(TokenExpiredError)
    async def token_expired_handler(request: Request, exc: TokenExpiredError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message, "code": "TOKEN_EXPIRED"},
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"Token has expired\""},
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message, "code": "INVALID_TOKEN"},
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    @app.exception_handler(TokenRevokedError)
    async def token_revoked_handler(request: Request, exc: TokenRevokedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message, "code": "TOKEN_REVOKED"},
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    @app.exception_handler(AccountLockedException)
    async def account_locked_handler(request: Request, exc: AccountLockedException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_423_LOCKED,
            content={"detail": exc.message, "code": "ACCOUNT_LOCKED"},
        )

    @app.exception_handler(AccountDisabledException)
    async def account_disabled_handler(request: Request, exc: AccountDisabledException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message, "code": "ACCOUNT_DISABLED"},
        )

    @app.exception_handler(InsufficientPermissionError)
    async def insufficient_permission_handler(request: Request, exc: InsufficientPermissionError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message, "details": exc.details, "code": "FORBIDDEN"},
        )

    @app.exception_handler(PasswordComplexityException)
    async def password_complexity_handler(request: Request, exc: PasswordComplexityException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "reasons": exc.details.get("reasons", []), "code": "WEAK_PASSWORD"},
        )

    @app.exception_handler(DuplicateEntityError)
    async def duplicate_entity_handler(request: Request, exc: DuplicateEntityError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message, "code": "DUPLICATE_ENTITY"},
        )

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message, "code": "NOT_FOUND"},
        )