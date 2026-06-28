"""Tests for the source-document object-store sync (epic #274, B3 / #279).

The transport (SigV4 + httpx) is validated against the published AWS reference vector;
all the upload-decision logic (rel→key, incremental skip, LFS skip, dry-run) is exercised
against an in-memory fake store — hermetic, no network.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from watermark.config import Settings
from watermark.site.objectstore import (
    ObjectStoreUnconfiguredError,
    R2Store,
    RemoteHead,
    SyncItem,
    corpus_items,
    md5_hex,
    plan_sync,
    run_sync,
    sigv4_authorization,
    store_from_settings,
)


class _FakeClient:
    """Records the request httpx would have sent; returns a canned response."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def request(
        self, method: str, url: str, *, headers: dict[str, str], content: bytes | None = None
    ) -> httpx.Response:
        self.calls.append({"method": method, "url": url, "headers": headers, "content": content})
        # raise_for_status() needs the originating request attached.
        self.response.request = httpx.Request(method, url)
        return self.response


def _store(client: _FakeClient) -> R2Store:
    return R2Store(
        account_id="acct123",
        bucket="bkt",
        access_key_id="AK",
        secret_access_key="SK",
        client=client,  # type: ignore[arg-type]
    )


def test_head_404_is_absent_not_an_error() -> None:
    store = _store(_FakeClient(httpx.Response(404)))
    assert store.head("x/y.pdf") is None


def test_head_200_parses_size_and_unquoted_etag() -> None:
    resp = httpx.Response(200, headers={"content-length": "1234", "etag": '"abc123"'})
    store = _store(_FakeClient(resp))
    head = store.head("x/y.pdf")
    assert head == RemoteHead(size=1234, etag="abc123")


def test_head_missing_content_length_defaults_to_zero() -> None:
    store = _store(_FakeClient(httpx.Response(200, headers={"etag": '"e"'})))
    assert store.head("k") == RemoteHead(size=0, etag="e")


def test_head_other_error_raises() -> None:
    store = _store(_FakeClient(httpx.Response(500)))
    with pytest.raises(httpx.HTTPStatusError):
        store.head("k")


def test_put_rewrites_metadata_underscores_and_sends_body() -> None:
    client = _FakeClient(httpx.Response(200))
    store = _store(client)
    store.put(
        "x/y.pdf", b"PDFBYTES", content_type="application/pdf", metadata={"sha_256": "deadbeef"}
    )
    call = client.calls[-1]
    assert call["method"] == "PUT"
    assert call["content"] == b"PDFBYTES"
    headers = call["headers"]
    assert isinstance(headers, dict)
    assert headers["content-type"] == "application/pdf"
    # underscores → hyphens for proxy safety, x-amz-meta- prefix.
    assert headers["x-amz-meta-sha-256"] == "deadbeef"


def test_put_raises_on_error_status() -> None:
    store = _store(_FakeClient(httpx.Response(403)))
    with pytest.raises(httpx.HTTPStatusError):
        store.put("k", b"b", content_type="text/plain", metadata={})


# --- SigV4 against the AWS reference vector -----------------------------------
def test_sigv4_matches_aws_reference_vector() -> None:
    """The documented AWS "GET Object" SigV4 example must produce its published signature."""
    empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    auth = sigv4_authorization(
        method="GET",
        canonical_uri="/test.txt",
        canonical_querystring="",
        headers={
            "host": "examplebucket.s3.amazonaws.com",
            "range": "bytes=0-9",
            "x-amz-content-sha256": empty,
            "x-amz-date": "20130524T000000Z",
        },
        payload_hash=empty,
        access_key="AKIAIOSFODNN7EXAMPLE",
        secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        amzdate="20130524T000000Z",
        datestamp="20130524",
        region="us-east-1",
        service="s3",
    )
    assert "Signature=f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41" in auth
    assert "SignedHeaders=host;range;x-amz-content-sha256;x-amz-date" in auth


# --- the work list ------------------------------------------------------------
def test_corpus_items_maps_rel_to_key_and_media_type(tmp_path: Path) -> None:
    docs = tmp_path / "documents"
    (docs / "recorder").mkdir(parents=True)
    (docs / "aedg").mkdir(parents=True)
    (docs / "recorder" / "deed.pdf").write_bytes(b"%PDF-1.4 body")
    (docs / "aedg" / "page.html").write_text("<html></html>", encoding="utf-8")

    items = {i.rel: i for i in corpus_items(docs)}
    assert items["recorder/deed.pdf"].media_type == "application/pdf"
    assert items["recorder/deed.pdf"].render_class == "pdf"
    assert items["aedg/page.html"].render_class == "html"
    assert items["recorder/deed.pdf"].path == docs / "recorder" / "deed.pdf"

    # --collection scopes to one slug.
    scoped = corpus_items(docs, collection="recorder")
    assert {i.rel for i in scoped} == {"recorder/deed.pdf"}


# --- the sync plan (incremental + LFS) ----------------------------------------
class _FakeStore:
    def __init__(self, heads: dict[str, RemoteHead]) -> None:
        self.heads = heads
        self.puts: list[tuple[str, str, dict[str, str], int]] = []

    def head(self, key: str) -> RemoteHead | None:
        return self.heads.get(key)

    def put(self, key: str, body: bytes, *, content_type: str, metadata: dict[str, str]) -> None:
        self.puts.append((key, content_type, metadata, len(body)))


def _item(tmp: Path, rel: str, body: bytes, *, available: bool = True) -> SyncItem:
    path = tmp / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return SyncItem(
        rel=rel,
        path=path,
        size=len(body),
        media_type="application/pdf",
        render_class="pdf",
        available=available,
    )


def test_plan_sync_skips_unchanged_and_lfs(tmp_path: Path) -> None:
    current = _item(tmp_path, "a.pdf", b"%PDF-aaaa")
    changed = _item(tmp_path, "b.pdf", b"%PDF-bbbb")  # remote exists but differs
    fresh = _item(tmp_path, "c.pdf", b"%PDF-cccc")  # not in remote
    pointer = _item(tmp_path, "d.pdf", b"version https://git-lfs...", available=False)

    store = _FakeStore(
        {
            "a.pdf": RemoteHead(size=current.size, etag=md5_hex(current.path)),
            "b.pdf": RemoteHead(size=999, etag="deadbeef"),
        }
    )
    plan = plan_sync([current, changed, fresh, pointer], store)
    assert {i.rel for i in plan.unchanged} == {"a.pdf"}
    assert {i.rel for i in plan.upload} == {"b.pdf", "c.pdf"}
    assert {i.rel for i in plan.lfs_skipped} == {"d.pdf"}


def test_run_sync_dry_run_uploads_nothing(tmp_path: Path) -> None:
    items = [_item(tmp_path, "a.pdf", b"%PDF-a"), _item(tmp_path, "b.pdf", b"%PDF-b")]
    store = _FakeStore({})
    plan, result = run_sync(items, store, dry_run=True)
    assert store.puts == []
    assert result.uploaded == 0
    assert {i.rel for i in plan.upload} == {"a.pdf", "b.pdf"}  # planned, not done


def test_run_sync_uploads_changed_and_stamps_metadata(tmp_path: Path) -> None:
    items = [_item(tmp_path, "a.pdf", b"%PDF-a"), _item(tmp_path, "b.pdf", b"%PDF-b")]
    store = _FakeStore({"a.pdf": RemoteHead(size=items[0].size, etag=md5_hex(items[0].path))})
    plan, result = run_sync(items, store)
    assert result.uploaded == 1
    assert len(plan.unchanged) == 1
    key, content_type, metadata, nbytes = store.puts[0]
    assert key == "b.pdf"
    assert content_type == "application/pdf"
    assert metadata == {"media_type": "application/pdf", "render_class": "pdf"}
    assert nbytes == items[1].size


# --- store factory / config ---------------------------------------------------
def test_store_from_settings_requires_credentials(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)  # no object-store creds
    try:
        store_from_settings(settings, target="remote")
    except ObjectStoreUnconfiguredError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ObjectStoreUnconfiguredError")


def test_store_from_settings_selects_bucket_by_target(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        documents_object_store_account_id="acct123",
        documents_object_store_access_key_id="AK",
        documents_object_store_secret_access_key="SK",
        documents_object_store_bucket="prod-bkt",
        documents_object_store_dev_bucket="dev-bkt",
    )
    remote = store_from_settings(settings, target="remote")
    local = store_from_settings(settings, target="local")
    assert remote._url("x/y.pdf").endswith("/prod-bkt/x/y.pdf")
    assert local._url("x/y.pdf").endswith("/dev-bkt/x/y.pdf")
    assert "acct123.r2.cloudflarestorage.com" in remote._url("k")
