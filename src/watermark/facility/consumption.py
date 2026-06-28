"""The campus annual-consumption assumption — one home for the load factor (#601).

The grid + economics scenarios all size a data-center campus's annual energy the same way:
``draw_mw x 8760 h x load_factor``. The load-factor assumption (0.9, near-flat 24x7) and the
GWh formula used to be redefined in four modules (grid/utility, grid/market, grid/policy,
economics/energy); they live here once so the assumption can't drift between them.

Each consumer keeps its own provenance *citation* prose (the issue references differ, and two
feed committed reference artifacts) — only the number and the formula are shared here.
"""

from __future__ import annotations

HOURS_PER_YEAR = 8760.0
# Data centers run near-flat (24x7); capacity utilization ~0.9. A stated modeling assumption,
# shared across the grid + economics scenarios (#91/#94/#95).
LOAD_FACTOR = 0.9


def annual_consumption_gwh(draw_mw: float) -> float:
    """Campus annual electricity consumption in GWh: ``draw_mw x 8760 h x load factor`` (MWh→GWh)."""
    return draw_mw * HOURS_PER_YEAR * LOAD_FACTOR / 1000.0
