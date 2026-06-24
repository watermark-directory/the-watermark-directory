"""Tests for ``output_dir_for_command`` — the catalog-derived cli ``--out`` (epic #631, #630).

Pins the resolution rules and, crucially, that the catalog-derived output dir matches the
historical hardcoded default for every wired command — so the two can't silently diverge now
that the command reads the catalog as its source of record.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from bosc.catalog import output_dir_for_command
from bosc.config import Settings


def _entry(settings: Settings, name: str, command: str, *relpaths: str) -> None:
    storage = "\n".join(f"- relpath: {r}\n  media_type: application/x-yaml" for r in relpaths)
    body = (
        textwrap.dedent(
            f"""\
        id: {name}
        title: T
        scope: reference
        producer:
          kind: connector
          source: x
          command: {command}
        refresh:
          cadence: static
        storage:
        """
        )
        + storage
    )
    path = settings.catalog_dir / "reference" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body + "\n", encoding="utf-8")


def _settings(tmp_path: Path) -> Settings:
    (tmp_path / "data").mkdir()
    return Settings(data_dir=tmp_path / "data")


# --- resolution rules ----------------------------------------------------------------------
def test_single_collection_resolves(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(settings, "echo-a", "npdes --basin maumee", "reference/echo/maumee-wwtp.potw.yaml")
    _entry(settings, "echo-b", "npdes", "reference/echo/great-miami-wwtp.potw.yaml")
    got = output_dir_for_command("npdes", settings=settings)
    assert got == settings.data_dir / "reference/echo"


def test_site_template_segment_is_dropped(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(
        settings,
        "eia-ce",
        "eia",
        "reference/eia/{site}/consumer-energy.yaml",
        "reference/eia/consumer-energy.yaml",
    )
    _entry(settings, "eia-ba", "eia", "reference/eia/ba-interchange.yaml")
    assert output_dir_for_command("eia", settings=settings) == settings.data_dir / "reference/eia"


def test_unknown_command_is_none(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(settings, "echo-a", "npdes", "reference/echo/x.yaml")
    assert output_dir_for_command("parcels", settings=settings) is None


def test_ambiguous_multi_collection_is_none(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(settings, "a", "grid", "reference/eia/grid-profile.yaml")
    _entry(settings, "b", "grid", "reference/pjm/zones.yaml")  # spans two collections
    assert output_dir_for_command("grid", settings=settings) is None


def test_verb_match_ignores_args(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    _entry(settings, "echo-a", "npdes --basin scioto --offline", "reference/echo/scioto.yaml")
    assert (
        output_dir_for_command("npdes", settings=settings) == settings.data_dir / "reference/echo"
    )


# --- anti-drift guard against the real catalog ---------------------------------------------
def test_wired_commands_match_their_historical_defaults() -> None:
    """The catalog now backs each wired command's --out; pin it to the legacy hardcoded path."""
    settings = Settings()
    expected = {
        "npdes": "reference/echo",
        "rsei": "reference/rsei",
        "gleif": "reference/gleif",
        "usaspending": "reference/usaspending",
    }
    for command, relpath in expected.items():
        got = output_dir_for_command(command, settings=settings)
        assert got == settings.data_dir / relpath, command
