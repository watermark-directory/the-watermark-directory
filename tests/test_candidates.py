"""Candidate-entity store: load/validate the committed inventory + site rendering."""

from __future__ import annotations

from pathlib import Path

from bosc import candidates
from bosc.pipeline.entities import EntityGraph
from bosc.site import candidates as site_candidates

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


def test_render_includes_caution_and_tiers() -> None:
    inv = candidates.load_cloud_consumer_candidates(ENTITIES)
    assert inv is not None
    page = site_candidates.render_candidates(inv, egraph=EntityGraph())
    assert "# Cloud-consumer candidates" in page
    assert "not customers or connections" in page.lower()
    assert "## Tier 1" in page
    # a known entity from the inventory renders
    assert "Ford Lima Engine Plant" in page


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


def test_render_defense_contractors_caution_and_seed() -> None:
    dcl = candidates.load_defense_contractors(ENTITIES)
    assert dcl is not None
    page = site_candidates.render_defense_contractors(dcl, egraph=EntityGraph())
    assert "# Defense contractors" in page
    assert "leads, not verdicts" in page.lower()
    assert "## Seed list" in page
    assert "Lockheed Martin" in page
