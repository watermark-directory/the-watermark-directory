"""Timeline assembly — merge dated events from every extraction into one order.

Phase C item 6. Each genre carries its own dates (a deed's recording date, an
NPDES permit's public-notice and comment-deadline dates, an OPC estimate's date);
this module pulls them into a single :class:`TimelineEvent` stream sorted into one
chronology, each event citing the artifact it came from.

Dates are transcribed from degraded scans, so parsing is lenient: a leading
``YYYY``, ``YYYY-MM``, or ``YYYY-MM-DD`` is enough to order on. Anything we can't
parse keeps its raw string and sinks to the end rather than being dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from bosc.logging import get_logger
from bosc.pipeline.corpus import Corpus, load_corpus

log = get_logger(__name__)

_DATE_RE = re.compile(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?")
# Sorts after any real date (year 9999) so undated events tail the chronology.
_UNDATED_KEY = (9999, 99, 99)


def _date_key(raw: str | None) -> tuple[int, int, int]:
    """A sortable ``(year, month, day)`` key from a loosely-formatted date."""
    if not raw:
        return _UNDATED_KEY
    match = _DATE_RE.search(raw)
    if not match:
        return _UNDATED_KEY
    year, month, day = match.groups()
    return (int(year), int(month or 0), int(day or 0))


@dataclass(frozen=True)
class TimelineEvent:
    """One dated event, traceable to the extraction(s) that supplied it."""

    date: str  # as transcribed (ISO where legible)
    category: str  # deed_recorded | npdes_public_notice | npdes_comment_deadline | opc_estimate
    title: str
    source: str  # primary extraction path, relative to data/extracted
    ref: str = ""  # logical id (instrument no / permit no) for cross-doc dedup
    parties: tuple[str, ...] = ()
    detail: str = ""
    also_sources: tuple[str, ...] = ()  # other artifacts reporting the same event

    @property
    def sort_key(self) -> tuple[tuple[int, int, int], str]:
        return (_date_key(self.date), self.category)


def _dedup(events: list[TimelineEvent]) -> list[TimelineEvent]:
    """Collapse the same real-world event reported by multiple artifacts.

    The corpus often holds several documents about one permit (permit + fact
    sheet + public notice), so an identical (ref, category, date) recurs. Keep
    the first, fold the rest's paths into ``also_sources``. Events with no ``ref``
    (nothing to key on) are passed through untouched.
    """
    seen: dict[tuple[str, str, tuple[int, int, int]], TimelineEvent] = {}
    out: list[TimelineEvent] = []
    for e in events:
        if not e.ref:
            out.append(e)
            continue
        key = (e.ref, e.category, _date_key(e.date))
        if key in seen:
            primary = seen[key]
            merged = replace(primary, also_sources=(*primary.also_sources, e.source))
            seen[key] = merged
            out[out.index(primary)] = merged
        else:
            seen[key] = e
            out.append(e)
    return out


def _deed_events(corpus: Corpus) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for rel, ex in corpus.deeds:
        d = ex.deed
        parties = tuple(d.grantors) + tuple(d.grantees)
        arrow = f"{', '.join(d.grantors) or '?'} → {', '.join(d.grantees) or '?'}"
        bits = [f"{len(d.parcel_ids)} parcel(s)"]
        if d.consideration is not None:
            bits.append(f"consideration {d.consideration:,}")
        events.append(
            TimelineEvent(
                date=d.recording_date or "",
                category="deed_recorded",
                title=f"{d.instrument_type or 'Deed'} {d.instrument_no or ''}: {arrow}".strip(),
                source=rel,
                ref=d.instrument_no or "",
                parties=parties,
                detail="; ".join(bits),
            )
        )
    return events


def _npdes_events(corpus: Corpus) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for rel, ex in corpus.permits:
        p = ex.permit
        parties = tuple(x for x in (p.applicant, p.facility_name) if x)
        label = f"NPDES {p.permit_no or '?'} ({p.facility_name or '?'})"
        if p.public_notice_date:
            events.append(
                TimelineEvent(
                    date=p.public_notice_date,
                    category="npdes_public_notice",
                    title=f"{label} — public notice",
                    source=rel,
                    ref=p.permit_no or "",
                    parties=parties,
                    detail=f"action {p.permit_action or '?'}; receiving {p.receiving_water or '?'}",
                )
            )
        if p.comment_period_end:
            events.append(
                TimelineEvent(
                    date=p.comment_period_end,
                    category="npdes_comment_deadline",
                    title=f"{label} — comment period ends",
                    source=rel,
                    ref=p.permit_no or "",
                    parties=parties,
                )
            )
    return events


def _opc_events(corpus: Corpus) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for rel, summary in corpus.summaries:
        meta = summary.meta
        if not meta.date:
            continue
        parties = tuple(x for x in (meta.estimator,) if x)
        events.append(
            TimelineEvent(
                date=meta.date,
                category="opc_estimate",
                title=f"OPC estimate: {meta.program or rel}",
                source=rel,
                parties=parties,
                detail=f"program total ~{summary.grand_total():,}" if summary.sub_estimates else "",
            )
        )
    return events


def build_timeline(corpus: Corpus | None = None) -> list[TimelineEvent]:
    """Assemble a single sorted chronology across the whole corpus."""
    corpus = corpus if corpus is not None else load_corpus()
    events = _deed_events(corpus) + _npdes_events(corpus) + _opc_events(corpus)
    events = _dedup(events)
    events.sort(key=lambda e: e.sort_key)
    log.info("timeline.built", events=len(events))
    return events
