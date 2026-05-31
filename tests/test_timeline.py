"""Tests for cross-document timeline assembly."""

from __future__ import annotations

from bosc.models import Deed, DeedExtraction, NpdesExtraction, NpdesPermit
from bosc.pipeline.corpus import Corpus
from bosc.pipeline.timeline import _date_key, build_timeline


def _deed(
    rel: str, *, no: str, date: str, grantor: str, grantee: str
) -> tuple[str, DeedExtraction]:
    return rel, DeedExtraction(
        doc_id=no,
        source_path=f"/x/{no}.pdf",
        kind="deed",
        dpi=200,
        deed=Deed(instrument_no=no, recording_date=date, grantors=[grantor], grantees=[grantee]),
    )


def _permit(rel: str, *, no: str, pn: str, end: str) -> tuple[str, NpdesExtraction]:
    return rel, NpdesExtraction(
        doc_id=no,
        source_path=f"/x/{rel}",
        kind="npdes",
        dpi=150,
        permit=NpdesPermit(
            permit_no=no, facility_name="WWTP", public_notice_date=pn, comment_period_end=end
        ),
    )


def test_date_key_parses_partial_dates() -> None:
    assert _date_key("2025-08-13") == (2025, 8, 13)
    assert _date_key("2024-03") == (2024, 3, 0)
    assert _date_key("2026") == (2026, 0, 0)
    assert _date_key(None) > (9000, 0, 0)  # undated sinks to the tail
    assert _date_key("n/a") > (9000, 0, 0)


def test_build_timeline_orders_and_labels() -> None:
    corpus = Corpus(
        deeds=[
            _deed(
                "recorder/late.deed.yaml",
                no="I2",
                date="2026-03-04",
                grantor="Seller",
                grantee="Acme LLC",
            ),
            _deed(
                "recorder/early.deed.yaml",
                no="I1",
                date="2025-08-13",
                grantor="Farm",
                grantee="Acme LLC",
            ),
        ],
        permits=[_permit("oepa/p.npdes.yaml", no="2PH1", pn="2025-04-28", end="2025-05-28")],
    )
    events = build_timeline(corpus)
    dates = [e.date for e in events]
    assert dates == sorted(dates, key=_date_key)  # chronological
    deed_events = [e for e in events if e.category == "deed_recorded"]
    assert {e.ref for e in deed_events} == {"I1", "I2"}
    assert "Acme LLC" in deed_events[0].parties
    cats = {e.category for e in events}
    assert {"deed_recorded", "npdes_public_notice", "npdes_comment_deadline"} <= cats


def test_build_timeline_dedups_same_event_across_sources() -> None:
    # Same permit + same public-notice date reported by two different artifacts.
    corpus = Corpus(
        permits=[
            _permit("oepa/permit.npdes.yaml", no="2PH00006", pn="2025-04-28", end="2025-05-28"),
            _permit("oepa/fact-sheet.npdes.yaml", no="2PH00006", pn="2025-04-28", end="2025-05-28"),
        ]
    )
    events = build_timeline(corpus)
    notices = [e for e in events if e.category == "npdes_public_notice"]
    assert len(notices) == 1  # collapsed to one event
    assert notices[0].also_sources == ("oepa/fact-sheet.npdes.yaml",)


def test_build_timeline_keeps_differing_dates_separate() -> None:
    # Same permit but two *different* public-notice dates must NOT collapse.
    corpus = Corpus(
        permits=[
            _permit("oepa/a.npdes.yaml", no="2PH00006", pn="2025-04-28", end="2025-05-28"),
            _permit("oepa/b.npdes.yaml", no="2PH00006", pn="2025-06-17", end="2025-05-28"),
        ]
    )
    notices = [e for e in build_timeline(corpus) if e.category == "npdes_public_notice"]
    assert {e.date for e in notices} == {"2025-04-28", "2025-06-17"}
