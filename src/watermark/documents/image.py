"""Raster image sources for the vision extractor (.png / .jpg / .tif) — #703.

A scanned image with no text layer is read straight into the forced-tool-use
vision extractor as a single page, with no OCR hint. The extractor pins its media
type to ``image/png`` (:data:`watermark.agent.extractor._MEDIA_TYPE`), so every accepted
raster is normalized to PNG bytes here — a ``.jpg`` / ``.tif`` is decoded and
re-encoded rather than passed through.

This is the alternate *source format* path; the document *kind* (deed, npdes, …)
is unchanged — an image NPDES scan extracts through the same ``extract_npdes`` as a
PDF one (see ``_read_doc`` in :mod:`watermark.pipeline.extract`).
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

# Raster suffixes the image read path accepts. The extractor only speaks PNG, so
# every one of these is normalized to PNG bytes by :func:`read_image_png`.
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def read_image_png(path: str | Path) -> bytes:
    """Load a raster source and return PNG bytes for the vision extractor.

    Any accepted raster is decoded and re-encoded as PNG — flattening CMYK /
    paletted / alpha / 1-bit modes to RGB — so a ``.jpg`` or ``.tif`` source is a
    valid ``image/png`` payload. Multi-frame TIFFs read their first frame (a single
    scanned sheet). The bytes are never trusted for *text*; the model reads the image.
    """
    with Image.open(path) as im:
        rgb = im.convert("RGB")
        buffer = io.BytesIO()
        rgb.save(buffer, format="PNG")
        return buffer.getvalue()
