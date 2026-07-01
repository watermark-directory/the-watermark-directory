"""Concept-glossary store (issue #68): frontmatter parsing, loading, export feed."""

from __future__ import annotations

from pathlib import Path

import pytest

from watermark.config import Settings
from watermark.site import concepts as concepts_mod

_CONCEPT = """---
title: 7Q10
kind: term
aliases: [7Q10 low flow]
tags: [hydrology, permitting]
summary: The design low-flow statistic.
related: [assimilative-capacity]
---

The **7Q10** is a low-flow statistic. See [[assimilative capacity]].
"""

_MINIMAL = """---
title: Bare Concept
---

Body only.
"""


def _write(tmp: Path, name: str, text: str) -> Path:
    path = tmp / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_concept_roundtrips_frontmatter(tmp_path: Path) -> None:
    item = concepts_mod.parse_concept(_write(tmp_path, "7q10.md", _CONCEPT))
    assert item.slug == "7q10"  # defaults to the file stem
    assert item.title == "7Q10"
    assert item.kind == "term"
    assert item.aliases == ["7Q10 low flow"]
    assert item.related == ["assimilative-capacity"]
    assert "[[assimilative capacity]]" in item.body


def test_defaults_for_minimal_frontmatter(tmp_path: Path) -> None:
    item = concepts_mod.parse_concept(_write(tmp_path, "bare.md", _MINIMAL))
    assert item.slug == "bare"
    assert item.kind == "concept"  # default
    assert item.aliases == [] and item.related == []


def test_unknown_frontmatter_key_is_rejected(tmp_path: Path) -> None:
    bad = "---\ntitle: A\nbogus_key: 1\n---\nbody\n"
    with pytest.raises(Exception):  # noqa: B017 - pydantic ValidationError
        concepts_mod.parse_concept(_write(tmp_path, "bad.md", bad))


def test_load_concepts_skips_readme_and_sorts_by_title(tmp_path: Path) -> None:
    _write(tmp_path, "README.md", "# not a concept")
    _write(tmp_path, "zed.md", "---\ntitle: Zed\n---\nz\n")
    _write(tmp_path, "alpha.md", "---\ntitle: Alpha\n---\na\n")
    items = concepts_mod.load_concepts(tmp_path)
    assert [c.title for c in items] == ["Alpha", "Zed"]


def test_load_concepts_missing_dir_is_empty(tmp_path: Path) -> None:
    assert concepts_mod.load_concepts(tmp_path / "nope") == []


def test_load_concepts_site_filter(tmp_path: Path) -> None:
    """Concepts with `sites:` frontmatter are only included for listed sites."""
    _write(tmp_path, "global.md", "---\ntitle: Global\n---\nbody\n")
    _write(tmp_path, "lima-only.md", "---\ntitle: Lima Only\nsites: [lima]\n---\nbody\n")
    # No site specified — site-tagged concepts are excluded (conservative: safer to omit
    # than to include Lima-specific content in an unknown-site bundle).
    items_no_site = concepts_mod.load_concepts(tmp_path)
    assert [c.title for c in items_no_site] == ["Global"]
    # Lima gets its own tagged concept.
    items_lima = concepts_mod.load_concepts(tmp_path, site="lima")
    assert {c.title for c in items_lima} == {"Global", "Lima Only"}
    # Another site only gets the global one.
    items_other = concepts_mod.load_concepts(tmp_path, site="urbana")
    assert [c.title for c in items_other] == ["Global"]


def test_committed_concept_store_loads_and_exports() -> None:
    """The committed data/concepts store parses and yields a non-empty feed."""
    settings = Settings(data_dir=Path(__file__).resolve().parent.parent / "data")
    items = concepts_mod.export_concepts(concepts_mod.load_concepts(settings.concepts_dir))
    slugs = {c.slug for c in items}
    assert {"7q10", "assimilative-capacity"} <= slugs  # the seed concepts are present
