"""Source-document access (PDF text + image rendering)."""

from __future__ import annotations

from bosc.documents.odg import OdgContent, read_odg
from bosc.documents.pdf import DEFAULT_DPI, PdfDocument

__all__ = ["DEFAULT_DPI", "OdgContent", "PdfDocument", "read_odg"]
