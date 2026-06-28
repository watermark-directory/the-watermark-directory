"""The hydrology finding record (mirrors the analyze-stage Finding)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HydroFinding:
    """One hydrology observation. Mirrors :class:`watermark.pipeline.analyze.Finding`."""

    subject: str
    check: str
    ok: bool
    detail: str

    def __str__(self) -> str:
        mark = "OK " if self.ok else "XX "
        return f"{mark} [{self.check}] {self.subject}: {self.detail}"
