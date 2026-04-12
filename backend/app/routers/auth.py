"""
Authentication dependency.

When auth.enabled = true in config.toml, all API routes require a Bearer token
in the Authorization header.  The token is compared using secrets.compare_digest
to prevent timing attacks.
"""
from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

_bearer = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    settings = get_settings()
    if not settings.auth_enabled:
        return  # auth disabled globally — allow all requests

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header (Bearer token required)",
        )

    expected = settings.api_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_TOKEN is not configured on the server",
        )

    # Constant-time comparison prevents timing-based token discovery
    if not secrets.compare_digest(credentials.credentials.encode(), expected.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
