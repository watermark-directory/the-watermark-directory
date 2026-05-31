"""Tests for the cross-document corpus loader."""

from __future__ import annotations

from pathlib import Path

import yaml

from bosc.config import Settings
from bosc.models import (
    BusinessFiling,
    Deed,
    DeedExtraction,
    NpdesExtraction,
    NpdesPermit,
    OPCMeta,
    OPCSummary,
    SosExtraction,
    SubEstimate,
)
from bosc.pipeline.corpus import load_corpus


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_load_corpus_classifies_by_shape(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)
    ex = settings.extracted_dir

    deed = DeedExtraction(
        doc_id="d",
        source_path="/x/a.pdf",
        kind="deed",
        dpi=200,
        deed=Deed(instrument_no="I1", grantees=["Acme LLC"]),
    )
    _write(ex / "recorder" / "a.deed.yaml", deed.to_yaml())

    permit = NpdesExtraction(
        doc_id="n",
        source_path="/x/b.pdf",
        kind="npdes",
        dpi=150,
        permit=NpdesPermit(permit_no="2PH00006"),
    )
    _write(ex / "oepa" / "b.npdes.yaml", permit.to_yaml())

    filing = SosExtraction(
        doc_id="s",
        source_path="/x/c.pdf",
        kind="sos",
        dpi=200,
        filing=BusinessFiling(entity_name="Tilted Gate LLC", jurisdiction="Delaware"),
    )
    _write(ex / "permits" / "c.sos.yaml", filing.to_yaml())

    summary = OPCSummary(
        meta=OPCMeta(date="2025-07-11", program="Roadwork"),
        sub_estimates=[SubEstimate(name="RB1", construction_subtotal=100, total=125)],
    )
    _write(ex / "aedg" / "s.summary.opc.yaml", yaml.safe_dump(summary.model_dump()))

    # Noise that must be skipped, not crash the load.
    _write(ex / "aedg" / "junk.yaml", "just: a string\n")

    corpus = load_corpus(settings)
    assert len(corpus.deeds) == 1
    assert len(corpus.permits) == 1
    assert len(corpus.filings) == 1
    assert len(corpus.summaries) == 1
    assert corpus.filings[0][1].filing.entity_name == "Tilted Gate LLC"
    assert not corpus.is_empty()
    rel, loaded_deed = corpus.deeds[0]
    assert rel == "recorder/a.deed.yaml"
    assert loaded_deed.deed.instrument_no == "I1"


def test_load_corpus_empty(tmp_path: Path) -> None:
    corpus = load_corpus(Settings(data_dir=tmp_path))
    assert corpus.is_empty()
    assert len(corpus) == 0
