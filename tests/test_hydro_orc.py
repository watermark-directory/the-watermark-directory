"""ORC connector: HTML parsing, breadcrumb/title resolution, offline fixture replay."""

from __future__ import annotations

from pathlib import Path

import pytest

from bosc.config import Settings
from bosc.hydrology.connectors import orc
from bosc.hydrology.connectors._cache import HydroOfflineError


def test_fetch_section_from_fixture(hydro_settings: Settings) -> None:
    sec = orc.fetch_section("149.43", settings=hydro_settings)
    assert sec is not None
    assert sec.number == "149.43"
    assert sec.heading == "Availability of public records for inspection and copying"
    assert sec.title_num == "1"
    assert sec.title_name == "State Government"
    assert sec.chapter_num == "149"
    assert "public record" in sec.text.lower()
    assert sec.url.endswith("/ohio-revised-code/section-149.43")


def test_named_slug_title_resolves(hydro_settings: Settings) -> None:
    # "General Provisions" is a named pseudo-title with no number.
    sec = orc.fetch_section("1.48", settings=hydro_settings)
    assert sec is not None
    assert sec.title_num is None
    assert sec.title_name == "General Provisions"
    assert sec.chapter_num == "1"


def test_fetch_chapter_inlines_all_sections(hydro_settings: Settings) -> None:
    sections = orc.fetch_chapter("149", settings=hydro_settings)
    assert len(sections) > 40  # chapter 149 has 60+ sections
    assert all(s.text for s in sections)  # every section carries its text
    by_num = {s.number: s for s in sections}
    assert by_num["149.01"].heading == "Official reports - number - filing"
    assert by_num["149.43"].chapter_num == "149"  # breadcrumb applies to all


def test_list_title_chapters_from_fixture(hydro_settings: Settings) -> None:
    chapters = orc.list_title_chapters("1", settings=hydro_settings)
    assert ("101", "General Assembly") in chapters
    assert any(num == "149" for num, _ in chapters)
    assert len(chapters) > 30


def test_scan_citations_requires_marker(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(
        "Per R.C. 149.43 and Ohio Revised Code 121.22; see also section 5709.85.\n"
        "Contract Section 8.3 is unrelated text without a code marker 4.2 here.\n",
        encoding="utf-8",
    )
    found = orc.scan_citations(tmp_path)
    assert "149.43" in found
    assert "121.22" in found
    assert "5709.85" in found
    assert "8.3" in found  # "Section 8.3" has the 'section' marker -> a candidate...
    assert "4.2" not in found  # ...but a bare number with no marker is not


def test_chapter_of_and_sort() -> None:
    assert orc.chapter_of("149.43") == "149"
    assert orc.chapter_of("5709.85") == "5709"
    assert orc._section_sort_key("149.43") < orc._section_sort_key("5709.85")


def test_offline_unfetched_section_raises(hydro_settings: Settings) -> None:
    with pytest.raises(HydroOfflineError):
        orc.fetch_section("4503.06", settings=hydro_settings)
