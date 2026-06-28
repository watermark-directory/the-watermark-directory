"""Shared provenance primitives for the evidence vocabulary (#60, #605).

The lightweight core the three provenance-tagged models speak —
:class:`watermark.site.feeds.Citation`, :class:`watermark.hypotheses.Citation`, and
:class:`watermark.hydrology.model.ProvenancedValue`. Each used to hand-mirror the same
``SourceKind``/``Confidence`` literals and the same ``verified`` predicate; those live here
once so the discipline can't drift. Kept dependency-free (no ``watermark.site`` / ``watermark.hydrology``
import) so any of them can import it without a cycle.
"""

from __future__ import annotations

from typing import Literal

# Where a value came from. document/connector are records or live gauges ([verified]);
# reference is a vendored published spec; assumption is a stated modeling input; derived
# is computed from other provenanced values.
SourceKind = Literal["document", "connector", "reference", "assumption", "derived"]
Confidence = Literal["high", "medium", "low"]


def source_is_verified(source_kind: SourceKind) -> bool:
    """True for a value grounded in a record or a live gauge (the ``[verified]`` tag).

    ``reference`` (a vendored published spec) is authoritative but is *not* a record about
    the subject; ``assumption``/``derived`` are stated/computed — so none are "verified" in
    the evidence-discipline sense.
    """
    return source_kind in ("document", "connector")
