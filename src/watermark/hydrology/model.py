"""Back-compat re-export of the hydrology models.

The Tier-0 hydrology models moved into the :mod:`watermark.hydrology.models` package
(split into cluster modules) in #600. This module re-exports the whole surface so
existing ``from watermark.hydrology.model import X`` imports keep working; new code may
import from :mod:`watermark.hydrology.models` directly.
"""

from __future__ import annotations

from watermark.hydrology.models import *  # noqa: F403
from watermark.hydrology.models import __all__ as __all__
