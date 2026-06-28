"""Candidate-entity store: load/validate the committed inventory."""

from __future__ import annotations

from pathlib import Path

from watermark import candidates

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTITIES = REPO_ROOT / "data" / "entities"


def test_committed_inventory_loads_and_is_marked() -> None:
    inv = candidates.load_cloud_consumer_candidates(ENTITIES)
    assert inv is not None
    assert len(inv.entities) >= 20
    # Every entity is a demand-fit candidate; tiers are 1-4.
    assert all(e.cloud_consumer_candidate for e in inv.entities)
    assert all(1 <= e.tier <= 4 for e in inv.entities)
    assert "what_this_is_not" in inv.meta  # the integrity caution is preserved


def test_inventories_live_under_profiles_subdir() -> None:
    # The curated inputs were moved under data/entities/profiles/.
    assert (ENTITIES / "profiles" / "cloud-consumer-candidates.yaml").is_file()
    assert (ENTITIES / "profiles" / "defense-contractors.yaml").is_file()


def test_defense_contractors_load_and_match() -> None:
    dcl = candidates.load_defense_contractors(ENTITIES)
    assert dcl is not None
    assert len(dcl.defense_contractors) >= 15
    assert "what_this_is_not" in dcl.meta
    names = {dc.name for dc in dcl.defense_contractors}
    assert "Boeing" in names
    # Case-insensitive substring matching against arbitrary names.
    hits = dcl.match(["The Boeing Company - Plant 4", "Jane Q. Public"])
    assert hits.get("Boeing") == ["The Boeing Company - Plant 4"]
    # The Harris false-positive guard: bare "HARRIS" must not match a person.
    assert dcl.match(["WILLIAM HARRIS"]) == {}
