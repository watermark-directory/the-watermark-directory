"""The peer-site corpus gate (#2137) — its verdict logic, and negative controls against the binary.

The binary-backed tests skip without a usable ``yidam``; the CI ``corpus`` job runs this file
explicitly beside the gate, so they are live there.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest

from watermark.config import Settings
from watermark.site import corpus_peers, yidam_cli

REPO_ROOT = Path(__file__).resolve().parents[1]
needs_binary = pytest.mark.skipif(
    not yidam_cli.usable(), reason="no yidam binary that speaks --format json"
)


def _base() -> Settings:
    return Settings(site="lima", data_dir=REPO_ROOT / "data")


def test_a_node_key_strips_the_corpus_prefix_suffix_and_line() -> None:
    assert corpus_peers._node_key(".yidam/corpus/question/lead-ohd000001.yml") == (
        "question/lead-ohd000001"
    )
    assert corpus_peers._node_key(".yidam/corpus/hypothesis/surveillance.yml:9") == (
        "hypothesis/surveillance"
    )


def test_every_known_gap_names_a_selectable_site() -> None:
    from watermark.site.doc_serving import exported_slugs

    assert set(corpus_peers.KNOWN_UNSOURCED) <= set(exported_slugs())


def test_an_unknown_slug_is_refused_before_anything_is_deleted(tmp_path: Path) -> None:
    """The slug becomes a path that is rmtree'd, so it is validated first."""
    keep = tmp_path / "keep"
    keep.mkdir()
    (keep / "evidence.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        corpus_peers.check_site("../keep", tmp_path / "work", _base())
    assert (keep / "evidence.txt").is_file()


@needs_binary
def test_the_known_gaps_hold_and_a_cleared_gap_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Positive control, then both ratchet directions, over the one peer carrying a known gap."""
    verdict = corpus_peers.check_site("troy-piqua", tmp_path, _base())
    assert verdict.passed, (verdict.errors, verdict.unexpected_unsourced, verdict.stale_known)

    # Unlisted, the gap is a regression: the gate must SEE it, not merely pass.
    monkeypatch.setitem(corpus_peers.KNOWN_UNSOURCED, "troy-piqua", frozenset())
    unlisted = corpus_peers.check_site("troy-piqua", tmp_path, _base())
    assert unlisted.unexpected_unsourced == ["question/lead-ohd000001"]
    assert not unlisted.passed

    # Listed but no longer firing, an entry is stale, so the list cannot over-excuse.
    monkeypatch.setitem(
        corpus_peers.KNOWN_UNSOURCED,
        "troy-piqua",
        frozenset({"question/lead-ohd000001", "question/lead-not-a-node"}),
    )
    stale = corpus_peers.check_site("troy-piqua", tmp_path, _base())
    assert stale.stale_known == ["question/lead-not-a-node"]
    assert not stale.passed


@needs_binary
def test_a_workdir_inside_the_repository_is_refused() -> None:
    """The binary resolves its root upward, and inside this repo would report on Lima's mirror.

    Written into the repo deliberately (an ignored path under `.yidam/`), because that is the
    case that happened: eight "peers" all reporting Lima's instance count, every one clean.
    """
    workdir = REPO_ROOT / ".yidam" / f"peers-test-{uuid.uuid4().hex[:8]}"
    try:
        with pytest.raises(RuntimeError, match="outside the repository"):
            corpus_peers.check_site("van-wert", workdir, _base())
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
