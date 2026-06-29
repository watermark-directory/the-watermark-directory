"""Unit tests for watermark.github — hermetic, no network."""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from watermark.config import Settings
from watermark.github._client import _TOKEN_REFRESH_BUFFER_S, GitHubAppClient
from watermark.github._permissions import AdminChecker

# ---------------------------------------------------------------------------
# Fixture RSA key (generated once per session, in-memory)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def rsa_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def rsa_private_key_pem(rsa_private_key: rsa.RSAPrivateKey) -> str:
    pem_bytes = rsa_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem_bytes.decode("utf-8")


def _app_settings(pem: str) -> Settings:
    return Settings.model_validate(
        {
            "github_app_id": "12345",
            "github_app_private_key": pem,
            "github_app_installation_id": "99",
        }
    )


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# GitHubAppClient.is_configured
# ---------------------------------------------------------------------------


def test_is_configured_true(rsa_private_key_pem: str) -> None:
    settings = _app_settings(rsa_private_key_pem)
    assert GitHubAppClient.is_configured(settings)


def test_is_configured_missing_key() -> None:
    settings = Settings.model_validate(
        {
            "github_app_id": "123",
            "github_app_installation_id": "99",
        }
    )
    assert not GitHubAppClient.is_configured(settings)


def test_is_configured_all_empty() -> None:
    assert not GitHubAppClient.is_configured(Settings())


# ---------------------------------------------------------------------------
# JWT structure
# ---------------------------------------------------------------------------


def test_jwt_structure(rsa_private_key_pem: str, rsa_private_key: rsa.RSAPrivateKey) -> None:
    settings = _app_settings(rsa_private_key_pem)
    client = GitHubAppClient(settings)

    raw_jwt = client._make_jwt()

    public_pem = rsa_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    payload = jwt.decode(
        raw_jwt,
        public_pem,  # type: ignore[arg-type]
        algorithms=["RS256"],
        options={"verify_exp": False},
    )

    assert payload["iss"] == "12345"
    now = int(time.time())
    # iat should be ~60 s in the past
    assert payload["iat"] <= now
    assert payload["iat"] >= now - 120
    # exp should be ~10 minutes in the future
    assert payload["exp"] > now
    assert payload["exp"] <= now + 700


# ---------------------------------------------------------------------------
# Token caching
# ---------------------------------------------------------------------------


def _future_expiry(seconds: int = 3600) -> str:
    dt = datetime.now(tz=UTC) + timedelta(seconds=seconds)
    return dt.isoformat()


def _mock_token_response(token: str = "ghs_test_token") -> MagicMock:
    resp = MagicMock()
    resp.status_code = 201
    resp.json.return_value = {
        "token": token,
        "expires_at": _future_expiry(),
    }
    resp.raise_for_status = MagicMock()
    return resp


def test_token_cache_avoids_second_request(rsa_private_key_pem: str) -> None:
    settings = _app_settings(rsa_private_key_pem)
    client = GitHubAppClient(settings)

    call_count = 0

    async def fake_post(url: str, headers: dict[str, str]) -> MagicMock:
        nonlocal call_count
        call_count += 1
        return _mock_token_response()

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    mock_http.post = AsyncMock(side_effect=fake_post)

    with patch("watermark.github._client.httpx.AsyncClient", return_value=mock_http):
        tok1 = _run(client.get_installation_token())
        tok2 = _run(client.get_installation_token())

    assert tok1 == tok2 == "ghs_test_token"
    # Second call must hit the cache, not the network.
    assert call_count == 1


def test_token_refresh_when_near_expiry(rsa_private_key_pem: str) -> None:
    settings = _app_settings(rsa_private_key_pem)
    client = GitHubAppClient(settings)

    call_count = 0
    tokens = ["ghs_first", "ghs_second"]

    async def fake_post(url: str, headers: dict[str, str]) -> MagicMock:
        nonlocal call_count
        resp = MagicMock()
        resp.json.return_value = {
            "token": tokens[call_count],
            "expires_at": _future_expiry(),
        }
        resp.raise_for_status = MagicMock()
        call_count += 1
        return resp

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    mock_http.post = AsyncMock(side_effect=fake_post)

    with patch("watermark.github._client.httpx.AsyncClient", return_value=mock_http):
        _run(client.get_installation_token())

    # Manually expire the cached token to within the refresh buffer.
    assert client._cached is not None
    almost_expired = datetime.now(tz=UTC) + timedelta(seconds=_TOKEN_REFRESH_BUFFER_S - 10)
    client._cached.expires_at = almost_expired

    with patch("watermark.github._client.httpx.AsyncClient", return_value=mock_http):
        tok2 = _run(client.get_installation_token())

    assert tok2 == "ghs_second"
    assert call_count == 2


# ---------------------------------------------------------------------------
# get_headers fallback
# ---------------------------------------------------------------------------


def test_get_headers_uses_app_token_when_configured(rsa_private_key_pem: str) -> None:
    settings = _app_settings(rsa_private_key_pem)
    client = GitHubAppClient(settings)

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    mock_http.post = AsyncMock(return_value=_mock_token_response("ghs_app_token"))

    with patch("watermark.github._client.httpx.AsyncClient", return_value=mock_http):
        headers = _run(client.get_headers())

    assert headers.get("Authorization") == "token ghs_app_token"


def test_get_headers_falls_back_to_pat() -> None:
    settings = Settings.model_validate({"GITHUB_TOKEN": "ghp_pat_token"})
    client = GitHubAppClient(settings)
    headers = _run(client.get_headers())
    assert headers.get("Authorization") == "Bearer ghp_pat_token"


def test_get_headers_no_auth_when_unconfigured() -> None:
    settings = Settings()
    client = GitHubAppClient(settings)
    headers = _run(client.get_headers())
    assert "Authorization" not in headers


# ---------------------------------------------------------------------------
# AdminChecker — allowlist
# ---------------------------------------------------------------------------


def test_admin_checker_is_admin() -> None:
    settings = Settings.model_validate({"admin_logins": "alice,bob"})
    checker = AdminChecker(settings)
    assert checker.is_admin("alice")
    assert checker.is_admin("bob")
    assert not checker.is_admin("carol")


def test_admin_checker_whitespace_tolerant() -> None:
    settings = Settings.model_validate({"admin_logins": " alice , bob "})
    checker = AdminChecker(settings)
    assert checker.is_admin("alice")
    assert checker.is_admin("bob")


def test_admin_checker_empty_logins() -> None:
    checker = AdminChecker(Settings())
    assert not checker.is_admin("anyone")


# ---------------------------------------------------------------------------
# AdminChecker — per-site allowlist
# ---------------------------------------------------------------------------


def test_site_admin_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WATERMARK_SITE_ADMIN_LOGINS_LIMA", "carol")
    checker = AdminChecker(Settings())
    assert checker.is_site_admin("carol", "lima")
    assert not checker.is_site_admin("carol", "fortwayne")


def test_admin_is_also_site_admin() -> None:
    settings = Settings.model_validate({"admin_logins": "admin_user"})
    checker = AdminChecker(settings)
    # A global admin should pass site-scoped checks for any site.
    assert checker.is_site_admin("admin_user", "lima")
    assert checker.is_site_admin("admin_user", "fortwayne")


# ---------------------------------------------------------------------------
# AdminChecker — require_admin / require_site_admin
# ---------------------------------------------------------------------------


def test_require_admin_passes() -> None:
    settings = Settings.model_validate({"admin_logins": "alice"})
    checker = AdminChecker(settings)
    checker.require_admin("alice")  # must not raise


def test_require_admin_denies() -> None:
    checker = AdminChecker(Settings())
    with pytest.raises(PermissionError, match="not in the admin allowlist"):
        checker.require_admin("carol")


def test_require_admin_none_with_trusted_flag() -> None:
    settings = Settings.model_validate({"github_app_trusted": True})
    checker = AdminChecker(settings)
    checker.require_admin(None)  # trusted App context — must not raise


def test_require_admin_none_without_trusted_flag() -> None:
    checker = AdminChecker(Settings())
    with pytest.raises(PermissionError, match="WATERMARK_GITHUB_APP_TRUSTED"):
        checker.require_admin(None)


def test_require_site_admin_none_trusted() -> None:
    settings = Settings.model_validate({"github_app_trusted": True})
    checker = AdminChecker(settings)
    checker.require_site_admin(None, "lima")  # must not raise


def test_require_site_admin_none_not_trusted() -> None:
    checker = AdminChecker(Settings())
    with pytest.raises(PermissionError, match="WATERMARK_GITHUB_APP_TRUSTED"):
        checker.require_site_admin(None, "lima")


# ---------------------------------------------------------------------------
# AdminChecker — check_team_membership stub
# ---------------------------------------------------------------------------


def test_check_team_membership_raises_not_implemented() -> None:
    checker = AdminChecker(Settings())
    with pytest.raises(NotImplementedError):
        checker.check_team_membership("alice", "watermark-directory", "admins")
