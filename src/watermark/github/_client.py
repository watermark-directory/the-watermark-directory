"""GitHub App authentication client (JWT → installation token)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import httpx
import jwt  # pyjwt[cryptography]

if TYPE_CHECKING:
    from watermark.config import Settings

_GH_ACCEPT = "application/vnd.github+json"
_GH_API_VERSION = "2022-11-28"
_JWT_DURATION_S = 600  # 10 minutes (GitHub max)
_TOKEN_REFRESH_BUFFER_S = 300  # refresh 5 minutes before expiry


@dataclass
class _CachedToken:
    token: str
    expires_at: datetime


class GitHubAppClient:
    """Async GitHub App client: signs JWTs and caches installation tokens.

    Generates a 10-minute RS256 JWT from the App's private key and exchanges it
    for an installation token (1-hour TTL). The token is cached on the instance and
    refreshed automatically when it is within 5 minutes of expiry.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cached: _CachedToken | None = None

    @staticmethod
    def is_configured(settings: Settings) -> bool:
        """Return True when all three App credentials are present."""
        return bool(
            settings.github_app_id
            and settings.github_app_private_key
            and settings.github_app_installation_id
        )

    def _make_jwt(self) -> str:
        now = int(time.time())
        payload = {
            # Back-date 60 s to tolerate clock skew between client and GitHub.
            "iat": now - 60,
            "exp": now + _JWT_DURATION_S,
            "iss": self._settings.github_app_id,
        }
        return jwt.encode(payload, self._settings.github_app_private_key, algorithm="RS256")

    def _token_valid(self) -> bool:
        if self._cached is None:
            return False
        now = datetime.now(tz=UTC)
        remaining = (self._cached.expires_at - now).total_seconds()
        return remaining > _TOKEN_REFRESH_BUFFER_S

    async def get_installation_token(self) -> str:
        """Return a valid installation token, refreshing if near expiry."""
        if self._token_valid() and self._cached is not None:
            return self._cached.token

        app_jwt = self._make_jwt()
        url = (
            f"{self._settings.github_base_url}"
            f"/app/installations/{self._settings.github_app_installation_id}/access_tokens"
        )
        headers = {
            "Accept": _GH_ACCEPT,
            "Authorization": f"Bearer {app_jwt}",
            "X-GitHub-Api-Version": _GH_API_VERSION,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers)
            resp.raise_for_status()
            data: dict[str, str] = resp.json()

        token = data["token"]
        expires_at = datetime.fromisoformat(data["expires_at"])
        self._cached = _CachedToken(token=token, expires_at=expires_at)
        return token

    async def get_headers(self) -> dict[str, str]:
        """Return Authorization + Accept headers, preferring App token over PAT.

        Falls back to the PAT (``GITHUB_TOKEN``) when App credentials are absent.
        Returns headers without an Authorization key when neither is configured.
        """
        settings = self._settings
        if self.is_configured(settings):
            token = await self.get_installation_token()
            auth = f"token {token}"
        elif settings.github_token:
            auth = f"Bearer {settings.github_token}"
        else:
            auth = ""

        headers: dict[str, str] = {
            "Accept": _GH_ACCEPT,
            "X-GitHub-Api-Version": _GH_API_VERSION,
        }
        if auth:
            headers["Authorization"] = auth
        return headers
