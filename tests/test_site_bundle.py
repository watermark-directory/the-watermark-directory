"""Integrity tests for the typed content bundle (issue #53, Tier 1 / #62).

Exports a full bundle to a temp dir off the committed corpus (hermetic, no network) and
asserts the contract holds: every feed validates against its JSON Schema, the manifest is
internally consistent, the committed schemas match what the models generate (drift guard),
and cross-feed references resolve (the bundle's "no orphaned references" — the spirit of
``tests/test_site_nav.py`` ported to the data tier).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema.validators import Draft202012Validator

from bosc.config import Settings
from bosc.pipeline.corpus import relpath_in_scope
from bosc.site.export import export_bundle
from bosc.sites import get_profile

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMITTED_SCHEMAS = REPO_ROOT / "data" / "site" / "bundle" / "schemas"
# The per-site offline fixture (#727): the trimmed Lima bundle the frontend build reads.
FRONTEND_SAMPLE = REPO_ROOT / "frontend" / "sample-bundle" / "lima"


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A freshly exported bundle, generated once for the module from the committed data."""
    out = tmp_path_factory.mktemp("bundle") / "b"
    settings = Settings(data_dir=REPO_ROOT / "data")
    export_bundle(settings, out_dir=out, generated_at="2026-01-01T00:00:00+00:00")
    return out


def _manifest(bundle: Path) -> dict[str, Any]:
    return json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))


def _feeds_by_name(bundle: Path) -> dict[str, dict[str, Any]]:
    return {f["name"]: f for f in _manifest(bundle)["feeds"]}


def _rows(bundle: Path, ref: dict[str, Any]) -> list[Any]:
    """The rows of a feed, regardless of media type (NDJSON / JSON array / single object)."""
    text = (bundle / ref["path"]).read_text(encoding="utf-8")
    if ref["media_type"] == "application/x-ndjson":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    parsed = json.loads(text)
    return parsed if ref["kind"] == "collection" else [parsed]


def test_manifest_validates_and_is_internally_consistent(bundle: Path) -> None:
    manifest = _manifest(bundle)
    schema = json.loads((bundle / "schemas" / "manifest.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(manifest)

    feeds = manifest["feeds"]
    assert manifest["feed_count"] == len(feeds)
    assert manifest["row_total"] == sum(f["count"] for f in feeds)
    names = [f["name"] for f in feeds]
    assert len(names) == len(set(names)), "duplicate feed names"
    for f in feeds:
        assert (bundle / f["path"]).is_file(), f"missing feed file {f['path']}"
        assert (bundle / f["schema"]).is_file(), f"missing schema {f['schema']}"


def test_every_feed_validates_against_its_schema(bundle: Path) -> None:
    manifest = _manifest(bundle)
    assert manifest["feeds"], "bundle has no feeds"
    for f in manifest["feeds"]:
        schema = json.loads((bundle / f["schema"]).read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        data_path = bundle / f["path"]
        if f["media_type"] == "application/x-ndjson":
            seen = 0
            for line in data_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    validator.validate(json.loads(line))
                    seen += 1
            assert seen == f["count"], f"{f['name']}: count {f['count']} != {seen} rows"
        else:
            doc = json.loads(data_path.read_text(encoding="utf-8"))
            validator.validate(doc)
            if f["kind"] == "collection":
                assert len(doc) == f["count"], f"{f['name']}: count mismatch"
            elif f["kind"] == "geojson":
                assert doc["type"] == "FeatureCollection"
                assert len(doc["features"]) == f["count"], f"{f['name']}: feature count mismatch"
            else:
                assert f["count"] == 1


def test_all_schemas_are_valid_draft_2020_12(bundle: Path) -> None:
    for path in sorted((bundle / "schemas").glob("*.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_committed_schemas_match_generated(bundle: Path) -> None:
    """The committed schemas/ must equal what the models generate — else `bosc export`."""
    generated = {p.name for p in (bundle / "schemas").glob("*.json")}
    committed = {p.name for p in COMMITTED_SCHEMAS.glob("*.json")}
    assert generated == committed, "committed schema set differs — run `bosc export`"
    for name in generated:
        gen = json.loads((bundle / "schemas" / name).read_text(encoding="utf-8"))
        com = json.loads((COMMITTED_SCHEMAS / name).read_text(encoding="utf-8"))
        assert gen == com, f"schema drift in {name} — regenerate with `bosc export`"


def test_cross_feed_references_resolve(bundle: Path) -> None:
    by_name = _feeds_by_name(bundle)
    entity_keys = {e["key"] for e in _rows(bundle, by_name["entities"])}

    # Every relationship endpoint is a real entity key.
    for rel in _rows(bundle, by_name["relationships"]):
        assert rel["src"] in entity_keys, f"relationship src {rel['src']} not in entities"
        assert rel["dst"] in entity_keys, f"relationship dst {rel['dst']} not in entities"

    # People / candidate cross-links resolve when present.
    for person in _rows(bundle, by_name["people"]):
        if person["entity_key"]:
            assert person["entity_key"] in entity_keys
    if "candidates" in by_name:
        for cand in _rows(bundle, by_name["candidates"]):
            if cand["entity_key"]:
                assert cand["entity_key"] in entity_keys

    # Defense-contractor matches are entity keys.
    if "defense-contractors" in by_name:
        defense = _rows(bundle, by_name["defense-contractors"])[0]
        for contractor in defense["contractors"]:
            for key in contractor["matched_entities"]:
                assert key in entity_keys, f"defense match {key} not in entities"

    # Every record cites an extraction artifact that exists (chain of custody).
    extracted = REPO_ROOT / "data" / "extracted"
    # The #276 record→source-document join must resolve to a real catalog entry.
    docs_by_rel = {
        e["rel"]: e for coll in _rows(bundle, by_name["documents"]) for e in coll["entries"]
    }
    joined = 0
    for record in _rows(bundle, by_name["records"]):
        assert (extracted / record["rel"]).exists(), f"record path missing: {record['rel']}"
        assert record["citation"]["source"] == record["rel"]
        src_rel = record.get("source_doc_rel")
        if src_rel is not None:
            assert src_rel in docs_by_rel, f"record {record['rel']} → uncatalogued source {src_rel}"
            assert record["source_doc_render_class"] == docs_by_rel[src_rel]["render_class"]
            joined += 1
    assert joined, "no record joined to a source document — the #276 join is dead"

    # Every timeline event's source resolves to a committed extraction (chain of custody).
    for event in _rows(bundle, by_name["timeline"]):
        if event.get("source"):
            assert (extracted / event["source"]).exists(), (
                f"timeline source missing: {event['source']}"
            )

    # Concept `related` siblings are real concept slugs (no orphaned wiki links).
    if "concepts" in by_name:
        concepts = _rows(bundle, by_name["concepts"])
        slugs = {c["slug"] for c in concepts}
        for c in concepts:
            for sib in c.get("related", []):
                assert sib in slugs, f"concept {c['slug']} relates to unknown concept {sib}"


def test_feed_slugs_are_unique(bundle: Path) -> None:
    """Slug-keyed feeds (the per-item page ids) must have no duplicates."""
    by_name = _feeds_by_name(bundle)
    for feed in ("people", "places", "concepts", "documents"):
        if feed not in by_name:
            continue
        slugs = [r["slug"] for r in _rows(bundle, by_name[feed])]
        assert len(slugs) == len(set(slugs)), f"{feed}: duplicate slugs"
        assert all(s and s == s.strip() for s in slugs), f"{feed}: blank/untrimmed slug"


def test_e14_watershed_and_imagery_geo_feeds_are_coherent(bundle: Path) -> None:
    """The E1.4 geo feeds (#61) for the #72 map exist and carry their metadata."""
    by_name = _feeds_by_name(bundle)

    watershed = json.loads((bundle / by_name["geo/watershed"]["path"]).read_text(encoding="utf-8"))
    assert watershed["features"], "watershed feed has no boundaries"
    for f in watershed["features"]:
        p = f["properties"]
        assert p["layer"] == "watershed"
        assert p["role"] == "area"
        assert str(p["huc"]).isdigit() and p["level"] in (8, 10, 12)
        assert p["name"], "watershed feature missing HU name"
    # Coarsest → finest so the finer subwatershed draws on top.
    levels = [f["properties"]["level"] for f in watershed["features"]]
    assert levels == sorted(levels)

    imagery = json.loads((bundle / by_name["geo/imagery"]["path"]).read_text(encoding="utf-8"))
    wayback = imagery["meta"]["wayback"]
    assert wayback["releases"], "imagery feed missing the dated Wayback ladder"
    assert "{release}" in wayback["tile_url_template"]
    assert all("date" in r and "release" in r for r in wayback["releases"])
    assert imagery["features"], "imagery feed missing an AOI footprint"
    assert all(f["properties"]["layer"] == "imagery" for f in imagery["features"])


def test_geo_features_carry_layer_metadata(bundle: Path) -> None:
    for name, ref in _feeds_by_name(bundle).items():
        if ref["kind"] != "geojson":
            continue
        fc = json.loads((bundle / ref["path"]).read_text(encoding="utf-8"))
        assert fc["meta"]["crs"].startswith("WGS84"), f"{name}: geometry must be WGS84 verbatim"
        for feature in fc["features"]:
            props = feature["properties"]
            assert props.get("layer"), f"{name}: feature missing layer"
            assert props.get("role") in ("area", "line", "point")


def _assert_fixture_tracks_export(fixture_dir: Path, exported_manifest: dict[str, Any]) -> None:
    """A committed ``sample-bundle/<slug>/`` fixture must not silently drift from its
    ``bosc … export`` (issue #179). It's a deliberately *trimmed* bundle, so its feed set is a
    subset — but the ``contract_version`` and ``site`` must match exactly, every feed it ships
    must still exist in the real export (catches a rename/removal), and the trimmed manifest must
    stay internally consistent. Refresh it (see the fixture's README.md) on drift.
    """
    sample = json.loads((fixture_dir / "manifest.json").read_text(encoding="utf-8"))

    assert sample["contract_version"] == exported_manifest["contract_version"], (
        f"{fixture_dir.name} contract_version {sample['contract_version']} != exported "
        f"{exported_manifest['contract_version']} — refresh the fixture"
    )
    assert sample["site"] == exported_manifest["site"], (
        f"{fixture_dir.name} fixture is for site {sample['site']!r} but exported {exported_manifest['site']!r}"
    )

    exported_feeds = {f["name"] for f in exported_manifest["feeds"]}
    stale = {f["name"] for f in sample["feeds"]} - exported_feeds
    assert not stale, f"{fixture_dir.name} fixture has feeds no longer produced by export: {stale}"

    # The trimmed manifest must stay internally consistent and its feed files present.
    assert sample["feed_count"] == len(sample["feeds"])
    assert sample["row_total"] == sum(f["count"] for f in sample["feeds"])
    for f in sample["feeds"]:
        assert (fixture_dir / f["path"]).is_file(), f"{fixture_dir.name} missing file {f['path']}"


def test_frontend_sample_bundle_tracks_the_export_contract(bundle: Path) -> None:
    """The committed Lima CI fixture tracks `bosc export` (the reference build)."""
    _assert_fixture_tracks_export(FRONTEND_SAMPLE, _manifest(bundle))


def test_fort_wayne_sample_bundle_tracks_the_export_contract(fort_wayne_bundle: Path) -> None:
    """The committed Fort Wayne fixture tracks `bosc --site fort-wayne export` (#741) — the
    first non-Lima sample bundle, so this also guards that a sibling fixture stays a real,
    per-site-scoped slice of its own export."""
    _assert_fixture_tracks_export(
        REPO_ROOT / "frontend" / "sample-bundle" / "fort-wayne", _manifest(fort_wayne_bundle)
    )


@pytest.fixture(scope="module")
def fort_wayne_bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A Fort Wayne bundle exported off the committed corpus — the sibling site used to
    prove per-site content scope (#762). Hermetic: no network, same committed data."""
    out = tmp_path_factory.mktemp("fwbundle") / "b"
    settings = Settings(data_dir=REPO_ROOT / "data", site="fort-wayne")
    export_bundle(settings, out_dir=out, generated_at="2026-01-01T00:00:00+00:00")
    return out


def test_non_reference_site_bundle_carries_no_lima_corpus(fort_wayne_bundle: Path) -> None:
    """A sibling site's per-site-scoped feeds must not inherit Lima's Allen-County-OH corpus.

    This is the #762 *content* guard the original count-based check missed: several feeds are
    built by readers that once globbed the whole extracted tree (the timeline civic builders,
    the entity-graph subdivision/relation-class overlays, the flat ``data/scenarios`` dir), so
    a non-Lima export silently inherited Lima's commissioners spine, township meetings, and
    Ottawa-River scenarios. Each is now bounded by the active site's ``corpus_relpaths``.

    The basin-/network-shared lenses (``network``, ``concepts``, the ``hypotheses`` *definitions*)
    are cross-site by design and not asserted here. The two site-tagged cross-site feeds —
    ``catalog`` and ``hypothesis-assessments`` — are narrowed for a sibling site (its own slice
    only) and asserted separately in :func:`test_sibling_bundle_narrows_cross_site_feeds`.
    """
    scope = get_profile("fort-wayne").corpus_relpaths
    assert scope is not None, "a sibling site must declare a corpus scope"

    # Every timeline event must cite a source inside Fort Wayne's corpus scope.
    feeds = _feeds_by_name(fort_wayne_bundle)
    for event in _rows(fort_wayne_bundle, feeds["timeline"]):
        assert relpath_in_scope(event["source"], scope), (
            f"timeline leaks an out-of-scope source: {event['source']}"
        )

    # No per-site feed may name a Lima-only collection (the markers these leaks left behind).
    lima_markers = (
        "commissioners/",
        "lacrpc/",
        "perry-township/",
        "american-township/",
        "shawnee-township/",
        "scenarios/baseline",
        "scenarios/buildout",
    )
    for name in ("timeline", "entities", "relationships", "hydrology-scenarios"):
        ref = feeds.get(name)
        if ref is None:
            continue
        text = (fort_wayne_bundle / ref["path"]).read_text(encoding="utf-8")
        for marker in lima_markers:
            assert marker not in text, f"feed {name!r} leaks Lima marker {marker!r}"


def test_sibling_bundle_narrows_cross_site_feeds(bundle: Path, fort_wayne_bundle: Path) -> None:
    """The two site-tagged cross-site feeds are strictly the sibling's own slice (#762).

    ``catalog`` and ``hypothesis-assessments`` form network-global sets, but each row is tagged
    with the site it belongs to. A sibling site's bundle carries only its own rows; the reference
    build (Lima) keeps the whole set — it's the network host the root ``/about/data`` and
    ``/research/hypotheses`` pages read, so narrowing it too would regress those views.
    """
    ref_feeds = _feeds_by_name(bundle)
    fw_feeds = _feeds_by_name(fort_wayne_bundle)

    # hypothesis-assessments: Lima carries the cross-site matrix; Fort Wayne only its own cells
    # (none committed yet → an empty feed, not other sites' rows).
    ref_cells = _rows(bundle, ref_feeds["hypothesis-assessments"])
    fw_cells = _rows(fort_wayne_bundle, fw_feeds["hypothesis-assessments"])
    assert {c["site"] for c in ref_cells} > {"lima"}, "reference build must keep the full matrix"
    assert all(c["site"] == "fort-wayne" for c in fw_cells), "sibling carries only its own cells"

    # catalog: the sibling drops Lima's pre-network legacy rows; the reference build keeps them.
    ref_scopes = {r["site_scope"] for r in _rows(bundle, ref_feeds["catalog"])}
    fw_scopes = {r["site_scope"] for r in _rows(fort_wayne_bundle, fw_feeds["catalog"])}
    assert "lima-legacy" in ref_scopes, "reference build keeps lima-legacy catalog rows"
    assert "lima-legacy" not in fw_scopes, "sibling bundle must drop lima-legacy catalog rows"


def test_approximate_markers_are_preserved_as_data(bundle: Path) -> None:
    """OPC figures transcribed with ``~`` surface as ``approximate_paths`` (issue #60)."""
    records = _rows(bundle, _feeds_by_name(bundle)["records"])
    opc = [r for r in records if r["group"] == "opc"]
    assert opc, "expected at least one OPC record"
    # The Tetra Tech roundabouts summary carries ~-marked program totals.
    assert any(r["approximate_paths"] for r in opc), "no ~ approximate markers preserved"
