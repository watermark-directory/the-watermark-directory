"""Read an OpenDocument Drawing (``.odg``) site plan.

An ``.odg`` is a vector drawing (a zip of XML), so its real content — titleblock
fields, the legend, street and feature labels — lives as *text* in ``content.xml``,
not as pixels. We extract those labels (authoritative) plus the embedded preview
thumbnail (a weak spatial overview); the extractor reads both, inverting the scan
hybrid (there the image leads and OCR hints; here the text leads).

Engineering ``.odg`` exports are large (an inline aerial basemap can push
``content.xml`` past 70 MB) and occasionally ship a bad CRC on that member, so the
text read is deliberately tolerant: bypass CRC validation and salvage whatever
decompresses rather than failing the whole document.
"""

from __future__ import annotations

import html
import re
import struct
import zipfile
import zlib
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from bosc.logging import get_logger

log = get_logger(__name__)

_LABEL_RE = re.compile(r"<text:(?:span|p)[^>]*>([^<]{1,200})</text:(?:span|p)>")
# A "meaningful" label has a real word; pure survey codes (RIM=828.75, spot
# elevations, contour numbers) are noise on a grading sheet.
_WORD_RE = re.compile(r"[A-Za-z]{3,}")
_THUMBNAIL = "Thumbnails/thumbnail.png"
_CONTENT = "content.xml"


@dataclass
class OdgContent:
    """Salvaged content of an ``.odg``: meaningful text labels + a thumbnail."""

    labels: list[str] = field(default_factory=list)
    thumbnail_png: bytes | None = None

    def label_text(self) -> str:
        return "\n".join(self.labels)


def _read_member_ignoring_crc(path: Path, info: zipfile.ZipInfo) -> bytes:
    """Inflate a zip member from raw bytes, bypassing zipfile's CRC validation.

    Reads the local-header to locate the compressed data, then inflates with a
    raw-DEFLATE ``decompressobj`` so a bad CRC or truncated tail yields the bytes
    decoded so far instead of raising.
    """
    with open(path, "rb") as fh:
        fh.seek(info.header_offset + 26)  # local header: name-len + extra-len fields
        name_len, extra_len = struct.unpack("<HH", fh.read(4))
        fh.seek(info.header_offset + 30 + name_len + extra_len)
        compressed = fh.read(info.compress_size)
    if info.compress_type != zipfile.ZIP_DEFLATED:
        return compressed
    decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
    try:
        return decompressor.decompress(compressed) + decompressor.flush()
    except zlib.error:  # pragma: no cover - corrupt tail: keep what inflated
        return decompressor.decompress(b"")


def read_odg(path: str | Path, *, max_labels: int = 140) -> OdgContent:
    """Extract meaningful text labels and the preview thumbnail from an ``.odg``.

    Labels are de-duplicated and ordered by frequency (titleblock and legend text
    repeats across sheets, so the most-repeated labels are the most structural),
    then capped at ``max_labels``.
    """
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        thumbnail: bytes | None = None
        try:
            thumbnail = zf.read(_THUMBNAIL)
        except (KeyError, zipfile.BadZipFile):  # pragma: no cover - optional member
            thumbnail = None
        content = _read_member_ignoring_crc(path, zf.getinfo(_CONTENT)).decode("utf-8", "ignore")

    counts: Counter[str] = Counter()
    for match in _LABEL_RE.findall(content):
        label = html.unescape(match).strip()
        if label and _WORD_RE.search(label):
            counts[label] += 1
    labels = [label for label, _ in counts.most_common(max_labels)]
    log.info("odg.read", path=str(path), labels=len(labels), thumbnail=bool(thumbnail))
    return OdgContent(labels=labels, thumbnail_png=thumbnail)
