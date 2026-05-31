"""Cross-check BOSC's deed extractions against the frozen Periplus parcel ledger.

`tests/fixtures/periplus-bosc-parcels.geojson` is Periplus's hand-curated land
ledger, copied unmodified from the fork point (see
`docs/reference/periplus/`). BOSC's deed extractor reads the *same conveyances*
from the raw recorder scans independently. This test asserts the two agree:
every parcel in the frozen ledger is reproduced by a committed deed extraction,
with a consistent grantee and prior owner. It is a regression guard — if a future
extractor change drops a parcel or flips an owner, this fails.

Match tokens are derived *from the ledger itself* (first word of each name), so
the test hardcodes no entity list and stays valid as the corpus grows.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_LEDGER = _HERE / "fixtures" / "periplus-bosc-parcels.geojson"
_DEEDS = _HERE.parent / "data" / "extracted" / "recorder"


def _parcel_to_deed() -> dict[str, dict[str, object]]:
    """Map every extracted parcel_id to its committed deed record."""
    mapping: dict[str, dict[str, object]] = {}
    for path in sorted(_DEEDS.glob("*.deed.yaml")):
        deed = yaml.safe_load(path.read_text(encoding="utf-8"))["deed"]
        for pid in deed.get("parcel_ids") or []:
            mapping[str(pid)] = deed
    return mapping


def test_deeds_reproduce_periplus_parcel_ledger() -> None:
    ledger = json.loads(_LEDGER.read_text(encoding="utf-8"))
    by_parcel = _parcel_to_deed()
    assert by_parcel, "no committed deed extractions found under data/extracted/recorder"

    missing: list[str] = []
    for feature in ledger["features"]:
        props = feature["properties"]
        pid = str(props["parcel_id"])
        deed = by_parcel.get(pid)
        if deed is None:
            missing.append(pid)
            continue

        grantees = " ".join(deed.get("grantees") or []).upper()
        grantors = " ".join(deed.get("grantors") or []).upper()
        # The frozen grantee's distinctive first token must appear in BOSC's grantee.
        grantee_token = str(props["grantee"]).split()[0].upper()
        assert grantee_token in grantees, f"{pid}: grantee {props['grantee']!r} vs {grantees!r}"
        # Likewise the prior owner's first token must appear in BOSC's grantors.
        prior_token = str(props["prior_owner"]).split()[0].upper()
        assert prior_token in grantors, f"{pid}: prior {props['prior_owner']!r} vs {grantors!r}"

    assert not missing, f"parcels in Periplus ledger missing from BOSC extractions: {missing}"
