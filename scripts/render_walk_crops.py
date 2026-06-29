"""Render committed scan crops for the guided walk's Record Teardown source viewer.

The walk's `① source` panel (frontend, issue #218) shows the *real* document
region instead of a placeholder. The source PDFs live under `data/documents/**`
(immutable, Git-LFS) and are far too large to ship to the static site, so we
render a small, focused PNG crop of the operative region and commit *that* under
`web/public/walk/crops/`. The crops are derived, regenerable artifacts —
this script is their provenance: it records the source PDF, the 0-based page,
and the crop box, so any crop can be reproduced byte-for-similar from the
immutable source.

Read-only with respect to `data/documents/**` (uses the read-only
`bosc.documents.PdfDocument`); only writes PNGs under the frontend public tree.

Usage (from the repo root):

    uv run python scripts/render_walk_crops.py

Pages are 0-based (printed `pdf_page == index + 1`). Add a crop by appending a
`CropSpec` below; the redaction overlay itself is drawn by the frontend from the
teardown's `scanCrop.redaction`, not baked into the pixels (so "the blank is the
evidence" stays legible and the source stays unaltered).
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from watermark.documents import PdfDocument

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = REPO_ROOT / "data" / "documents"
OUT_DIR = REPO_ROOT / "frontend" / "public" / "walk" / "crops"

# Final crop width on the page; the source card is ~440px wide, 2x for retina.
TARGET_WIDTH = 900
RENDER_DPI = 150


@dataclass(frozen=True)
class CropSpec:
    """One committed crop: source PDF, 0-based page, fractional crop box, output."""

    out_name: str
    source_pdf: str
    page_index: int
    # Crop box as fractions of the rendered page (left, top, right, bottom).
    box: tuple[float, float, float, float]
    note: str


CROPS: list[CropSpec] = [
    CropSpec(
        out_name="opc-summary.png",
        source_pdf="aedg/PRR-01-bundle.ocr.pdf",
        page_index=317,  # printed pdf_page 318 — the Tetra Tech OPC summary sheet
        box=(0.02, 0.04, 0.99, 0.82),
        note="OPC summary: 6 corridor line items + CONSTRUCTION TOTAL $14,223,081",
    ),
    CropSpec(
        out_name="dte100-blank.png",
        source_pdf="aedg/PRR-01-bundle.ocr.pdf",
        page_index=157,  # index p.158 — Brenneman DTE-100 conveyance-fee statement
        box=(0.03, 0.40, 0.99, 0.74),
        note="DTE-100 value lines 1-9: the conveyance-value dollar column produced BLANK",
    ),
]


def render_crop(spec: CropSpec) -> Path:
    """Render one crop spec to a committed PNG and return its path."""
    pdf_path = DOCUMENTS / spec.source_pdf
    doc = PdfDocument(pdf_path)
    try:
        page = Image.open(io.BytesIO(doc.render_page_png(spec.page_index, dpi=RENDER_DPI)))
    finally:
        doc.close()

    width, height = page.size
    left, top, right, bottom = spec.box
    crop = page.crop(
        (int(left * width), int(top * height), int(right * width), int(bottom * height))
    )

    if crop.width > TARGET_WIDTH:
        scale = TARGET_WIDTH / crop.width
        crop = crop.resize((TARGET_WIDTH, round(crop.height * scale)), Image.LANCZOS)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / spec.out_name
    # These are black-on-white document scans — grayscale is faithful and much
    # smaller than RGB for a web source thumbnail.
    crop.convert("L").save(out_path, format="PNG", optimize=True)
    return out_path


def main() -> None:
    for spec in CROPS:
        out_path = render_crop(spec)
        size_kb = out_path.stat().st_size / 1024
        print(f"wrote {out_path.relative_to(REPO_ROOT)} ({size_kb:.0f} KB) — {spec.note}")


if __name__ == "__main__":
    main()
