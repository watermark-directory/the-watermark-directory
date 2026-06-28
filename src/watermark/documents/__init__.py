"""Source-document access (PDF text + image rendering, ODG labels, raster sources)."""

from __future__ import annotations

from watermark.documents.image import IMAGE_SUFFIXES, read_image_png
from watermark.documents.odg import OdgContent, read_odg
from watermark.documents.pdf import DEFAULT_DPI, PdfDocument

__all__ = [
    "DEFAULT_DPI",
    "IMAGE_SUFFIXES",
    "OdgContent",
    "PdfDocument",
    "read_image_png",
    "read_odg",
]
