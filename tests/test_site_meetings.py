"""The shared committed-summaries loader."""

from __future__ import annotations

from pathlib import Path

import yaml

from bosc.civic.summarize import load_committed_summaries
from bosc.config import Settings


def _seed(settings: Settings, slug: str, meetings: list[dict[str, object]]) -> None:
    p = settings.extracted_dir / slug / "meetings" / "meeting-summaries.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump({"meta": {"slug": slug}, "meetings": meetings}), encoding="utf-8")


def test_load_committed_summaries_groups_and_sorts(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)
    _seed(settings, "lacrpc", [{"date": "2026-04-23", "kind": "minutes", "filename": "b.pdf"}])
    _seed(
        settings,
        "american-township",
        [
            {"date": "2024-12-09", "kind": "minutes", "filename": "later.docx"},
            {"date": "2024-11-25", "kind": "minutes", "filename": "earlier.docx"},
        ],
    )
    loaded = load_committed_summaries(settings)
    assert len(loaded) == 3
    # Sorted by (slug, date): american-township earlier first, then later, then lacrpc.
    assert [m["filename"] for _, m in loaded] == ["earlier.docx", "later.docx", "b.pdf"]
