"""Back-compat re-export of the hydrology models.

The Tier-0 hydrology models moved into the :mod:`bosc.hydrology.models` package
(split into cluster modules) in #600. This module re-exports the whole surface so
existing ``from bosc.hydrology.model import X`` imports keep working; new code may
import from :mod:`bosc.hydrology.models` directly.
"""

from __future__ import annotations

from bosc.hydrology.models import *  # noqa: F403
from bosc.hydrology.models import __all__ as __all__
