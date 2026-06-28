"""Pure record-classification helpers in site/records.py (#620)."""

from __future__ import annotations

from watermark.site.records import _approx_paths, _classify, _Record, _record_title


def test_approx_paths_finds_every_tilde_scalar() -> None:
    # The ~-marker survives in the raw YAML as a string; _approx_paths reports its dotted
    # path so the bundle carries the approximate flag as data (#60 / #612).
    data = {
        "total": "~14223081",
        "precise": 600000,
        "section": {"drainage": "~1068530", "roadway": "12000"},
        "items": ["~5", "9", {"q": "~2"}],
    }
    assert _approx_paths(data) == ["total", "section.drainage", "items.0", "items.2.q"]
    assert _approx_paths({"a": "1.5"}) == []  # no marker → nothing
    assert _approx_paths("~9") == [""]  # a bare scalar


def test_classify_recognizes_block_genres_and_opc() -> None:
    assert _classify({"deed": {"grantee": "X"}}) == ("deeds", {"grantee": "X"})
    assert _classify({"permit": {"permit_no": "2PH"}}) == ("permits-npdes", {"permit_no": "2PH"})
    assert _classify({"action": {"agency": "OEPA"}})[0] == "permits-epa"
    # OPC is whole-document: the estimate block (if present) is the payload.
    assert _classify({"estimate": {"name": "OPC"}}) == ("opc", {"name": "OPC"})
    # Unrecognized shapes / non-dicts → None.
    assert _classify({"unknown": 1}) is None
    assert _classify(["not", "a", "dict"]) is None


def test_record_title_prefers_the_most_identifying_field() -> None:
    rec = _Record(
        rel="oepa/x.yaml",
        group="permits-npdes",
        data={},
        payload={"facility_name": "American II WWTP"},
    )
    assert _record_title(rec) == "American II WWTP"
    # Falls back to meta.program, then the file stem.
    rec2 = _Record(
        rel="aedg/roundabouts.opc.yaml",
        group="opc",
        data={},
        payload={"meta": {"program": "BOSC Roadwork"}},
    )
    assert _record_title(rec2) == "BOSC Roadwork"
    rec3 = _Record(rel="misc/cole-street.yaml", group="opc", data={}, payload={})
    assert _record_title(rec3) == "cole-street"
