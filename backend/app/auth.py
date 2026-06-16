from __future__ import annotations

import secrets
from dataclasses import dataclass

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from backend.config.settings import get_settings


# The header-based scheme is automatically exposed in FastAPI's OpenAPI schema
# when the dependency is used with Security(...) on protected endpoints.
api_key_header = APIKeyHeader(
    name="X-API-Key",
    scheme_name="ApiKeyAuth",
    description="API key required to access protected data and model endpoints.",
    auto_error=False,
)


@dataclass(slots=True)
class AuthenticatedPrincipal:
    """Minimal identity object returned by the auth dependency."""

    username: str
    auth_scheme: str


def require_api_key(api_key: str | None = Security(api_key_header)) -> AuthenticatedPrincipal:
    """
    Validate the API key sent by the client.

    This dependency is intentionally lightweight so it can secure sensitive
    endpoints without changing the business logic of the application.
    """

    settings = get_settings()
    expected_api_key = settings.api_key
    if api_key and secrets.compare_digest(api_key, expected_api_key):
        return AuthenticatedPrincipal(username=settings.demo_username, auth_scheme="api_key")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
        headers={"WWW-Authenticate": "ApiKey"},
    )

