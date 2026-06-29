"""Admin and site-admin permission checks for GitHub write operations."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from watermark.config import Settings

# Per-site admin lists are keyed by the dynamic site slug and cannot be enumerated
# in Settings, so they are read directly from os.environ here.
_SITE_ADMIN_PREFIX = "WATERMARK_SITE_ADMIN_LOGINS_"


def _parse_logins(raw: str) -> list[str]:
    return [s.strip() for s in raw.split(",") if s.strip()]


class AdminChecker:
    """Check whether a GitHub login is an admin or site-admin.

    Permission sources (in priority order):
    - ``WATERMARK_ADMIN_LOGINS`` — comma-separated global admin logins
    - ``WATERMARK_SITE_ADMIN_LOGINS_<SLUG>`` — per-site admin logins (e.g.
      ``WATERMARK_SITE_ADMIN_LOGINS_LIMA=alice,bob``)
    - ``WATERMARK_GITHUB_APP_TRUSTED`` — when True, a missing caller identity
      (``GITHUB_ACTOR`` not set) is treated as a trusted App-as-operator context

    The ``check_team_membership`` stub is provided as a seam for a future
    GitHub Teams API integration.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._admins = frozenset(_parse_logins(settings.admin_logins))

    def _site_admins(self, site: str) -> frozenset[str]:
        raw = os.environ.get(f"{_SITE_ADMIN_PREFIX}{site.upper()}", "")
        return frozenset(_parse_logins(raw))

    def resolve_caller(self) -> str | None:
        """Return the GitHub login of the current actor, or None if unavailable.

        Reads ``GITHUB_ACTOR`` (set by the GH Actions runner; not WATERMARK-prefixed
        so it cannot be represented in Settings).
        """
        actor = os.environ.get("GITHUB_ACTOR", "").strip()
        return actor or None

    def is_admin(self, login: str) -> bool:
        """Return True if login is in the global admin allowlist."""
        return login in self._admins

    def is_site_admin(self, login: str, site: str) -> bool:
        """Return True if login is an admin or in the per-site allowlist."""
        return self.is_admin(login) or login in self._site_admins(site)

    def require_admin(self, login: str | None) -> None:
        """Raise PermissionError if login is not an admin.

        A None login passes when ``WATERMARK_GITHUB_APP_TRUSTED`` is True
        (App-as-operator GH Actions context).
        """
        if login is None:
            if self._settings.github_app_trusted:
                return
            raise PermissionError(
                "No caller identity (GITHUB_ACTOR not set) and "
                "WATERMARK_GITHUB_APP_TRUSTED is not enabled."
            )
        if not self.is_admin(login):
            raise PermissionError(
                f"GitHub login {login!r} is not in the admin allowlist (WATERMARK_ADMIN_LOGINS)."
            )

    def require_site_admin(self, login: str | None, site: str) -> None:
        """Raise PermissionError if login is not admin or site-admin for site.

        A None login passes when ``WATERMARK_GITHUB_APP_TRUSTED`` is True.
        """
        if login is None:
            if self._settings.github_app_trusted:
                return
            raise PermissionError(
                "No caller identity (GITHUB_ACTOR not set) and "
                "WATERMARK_GITHUB_APP_TRUSTED is not enabled."
            )
        if not self.is_site_admin(login, site):
            raise PermissionError(
                f"GitHub login {login!r} is not an admin or site-admin for {site!r}."
            )

    def check_team_membership(self, login: str, org: str, team_slug: str) -> bool:
        """Check GitHub Teams API membership for login.

        Not yet implemented — raises to signal the seam exists but is unfilled.
        Use WATERMARK_ADMIN_LOGINS in the meantime.
        """
        raise NotImplementedError(
            "GitHub Teams API membership check is not yet implemented. "
            f"Cannot verify {login!r} in {org}/{team_slug}. "
            "Use WATERMARK_ADMIN_LOGINS instead."
        )
