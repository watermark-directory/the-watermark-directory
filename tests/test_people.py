"""Person-profile store: frontmatter parsing + the expanded-research gate."""

from __future__ import annotations

from pathlib import Path

import pytest

from watermark import people

_PROFILE = """---
name: Scott J. Ziance
entity_key: SCOTT ZIANCE
aliases: [Scott Ziance]
roles: [organizer, permit contact]
expanded_research: true
sources:
  - data/extracted/permits/3789048.epa.yaml
---

Body prose about how he appears in the record.
"""

_TRACKED_ONLY = """---
name: Jane Tracked
expanded_research: false
---

Tracked but not published.
"""


def _write(tmp: Path, name: str, text: str) -> Path:
    path = tmp / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_profile_roundtrips_frontmatter(tmp_path: Path) -> None:
    prof = people.parse_profile(_write(tmp_path, "scott-ziance.md", _PROFILE))
    assert prof.name == "Scott J. Ziance"
    assert prof.slug == "scott-ziance"  # from file stem
    assert prof.entity_key == "SCOTT ZIANCE"
    assert prof.expanded is True
    assert "appears in the record" in prof.body
    assert prof.front.aliases == ["Scott Ziance"]


def test_entity_key_defaults_to_normalized_name(tmp_path: Path) -> None:
    prof = people.parse_profile(_write(tmp_path, "x.md", _TRACKED_ONLY))
    assert prof.entity_key == "JANE TRACKED"  # normalize_name(name), no explicit key
    assert prof.expanded is False


def test_unknown_frontmatter_key_is_rejected(tmp_path: Path) -> None:
    bad = "---\nname: A\nbogus_key: 1\n---\nbody\n"
    with pytest.raises(Exception):  # noqa: B017 - pydantic ValidationError
        people.parse_profile(_write(tmp_path, "bad.md", bad))


def test_missing_frontmatter_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="frontmatter"):
        people.parse_profile(_write(tmp_path, "nofm.md", "# just a heading\n"))


def test_load_people_skips_readme_and_sorts(tmp_path: Path) -> None:
    _write(tmp_path, "README.md", "# not a profile")
    _write(tmp_path, "scott-ziance.md", _PROFILE)
    _write(tmp_path, "jane.md", _TRACKED_ONLY)
    loaded = people.load_people(tmp_path)
    assert [p.name for p in loaded] == ["Jane Tracked", "Scott J. Ziance"]  # by name
