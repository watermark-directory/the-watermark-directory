"""The cross-document layer — load every committed extraction into one corpus.

Stages 1-2 produce per-document artifacts under ``data/extracted/**`` (one YAML
per deed, NPDES permit, or OPC page). Phase C reasons *across* them — a timeline,
an entity graph — so it first needs them all in memory as typed models. This
module is that loader: walk the extracted tree, classify each file by its content
shape (not just its name), and validate it back into the model that produced it.

Each loaded item is tagged with its ``rel_path`` (relative to ``data/extracted``)
so downstream analysis can cite the artifact it came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from bosc.config import Settings, get_settings
from bosc.logging import get_logger
from bosc.models import (
    DeedExtraction,
    EpaExtraction,
    NpdesExtraction,
    OPCSummary,
    PageExtraction,
    SosExtraction,
)

log = get_logger(__name__)


@dataclass(frozen=True)
class Corpus:
    """All committed extractions, grouped by genre and tagged with their path.

    Each entry is a ``(rel_path, model)`` pair where ``rel_path`` is relative to
    ``data/extracted`` — the citable provenance for any cross-document finding.
    """

    deeds: list[tuple[str, DeedExtraction]] = field(default_factory=list)
    permits: list[tuple[str, NpdesExtraction]] = field(default_factory=list)
    filings: list[tuple[str, SosExtraction]] = field(default_factory=list)
    actions: list[tuple[str, EpaExtraction]] = field(default_factory=list)
    estimates: list[tuple[str, PageExtraction]] = field(default_factory=list)
    summaries: list[tuple[str, OPCSummary]] = field(default_factory=list)

    def __len__(self) -> int:
        return (
            len(self.deeds)
            + len(self.permits)
            + len(self.filings)
            + len(self.actions)
            + len(self.estimates)
            + len(self.summaries)
        )

    def is_empty(self) -> bool:
        return len(self) == 0


def _classify(data: Any) -> str | None:
    """Identify an extraction by its top-level keys (shape, not filename).

    Returns one of ``deed`` / ``npdes`` / ``opc_page`` / ``opc_summary``, or
    ``None`` for anything that isn't a recognized extraction.
    """
    if not isinstance(data, dict):
        return None
    if "deed" in data:
        return "deed"
    if "permit" in data:
        return "npdes"
    if "filing" in data:
        return "sos"
    if "action" in data:
        return "epa"
    if "estimate" in data:
        return "opc_page"
    if "sub_estimates" in data or "meta" in data:
        return "opc_summary"
    return None


def load_corpus(settings: Settings | None = None) -> Corpus:
    """Load and validate every extraction under ``data/extracted`` into a Corpus.

    Files that fail to parse or validate are logged and skipped (the corpus is a
    best-effort view; one malformed artifact must not blind the whole layer).
    """
    settings = settings or get_settings()
    extracted = settings.extracted_dir
    corpus = Corpus()
    if not extracted.exists():
        log.warning("corpus.no_extracted_dir", path=str(extracted))
        return corpus

    for path in sorted(extracted.rglob("*.yaml")):
        rel = str(path.relative_to(extracted))
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            log.warning("corpus.bad_yaml", path=rel, error=str(exc).splitlines()[0])
            continue
        kind = _classify(data)
        try:
            if kind == "deed":
                corpus.deeds.append((rel, DeedExtraction.model_validate(data)))
            elif kind == "npdes":
                corpus.permits.append((rel, NpdesExtraction.model_validate(data)))
            elif kind == "sos":
                corpus.filings.append((rel, SosExtraction.model_validate(data)))
            elif kind == "epa":
                corpus.actions.append((rel, EpaExtraction.model_validate(data)))
            elif kind == "opc_page":
                corpus.estimates.append((rel, PageExtraction.model_validate(data)))
            elif kind == "opc_summary":
                corpus.summaries.append((rel, OPCSummary.model_validate(data)))
            else:
                log.warning("corpus.unrecognized", path=rel)
        except Exception as exc:  # validation errors are per-file; keep loading the rest
            log.warning("corpus.invalid", path=rel, kind=kind, error=str(exc).splitlines()[0])

    log.info(
        "corpus.loaded",
        deeds=len(corpus.deeds),
        permits=len(corpus.permits),
        filings=len(corpus.filings),
        actions=len(corpus.actions),
        estimates=len(corpus.estimates),
        summaries=len(corpus.summaries),
    )
    return corpus
