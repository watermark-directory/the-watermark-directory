"""Multi-hypothesis layer: the default set reproduces run_scenarios' buildout
numbers (regression lock), and Shawnee II's theorized FM-3 is held out unless a
hypothesis explicitly promotes it.
"""

from __future__ import annotations

from bosc.config import Settings
from bosc.hydrology import hypothesis as hyp_stage
from bosc.pipeline import hydrology as hydro_stage


def test_default_buildout_matches_run_scenarios(hydro_settings: Settings) -> None:
    """`buildout-confirmed` must equal run_scenarios' buildout net loss (no drift)."""
    _, build, _ = hydro_stage.run_scenarios(settings=hydro_settings, live=False)
    comparison = hyp_stage.run_hypotheses(settings=hydro_settings, live=False)
    confirmed = next(h for h in comparison.hypotheses if h.hypothesis.name == "buildout-confirmed")
    assert confirmed.result.consumptive_loss.value == build.consumptive_loss.value


def test_shawnee_held_out_unless_promoted(hydro_settings: Settings) -> None:
    comparison = hyp_stage.run_hypotheses(settings=hydro_settings, live=False)
    by_name = {h.hypothesis.name: h for h in comparison.hypotheses}

    # Default confirmed routing holds Shawnee II's FM-3 out.
    confirmed = by_name["buildout-confirmed"]
    assert any("shawnee" in r.via.lower() for r in confirmed.excluded_theorized)
    assert all("shawnee" not in r.via.lower() for r in confirmed.routing_applied)

    # The what-if promotes it: Shawnee II joins the built routes, nothing held out.
    fm3 = by_name["buildout-with-fm3"]
    assert any("shawnee" in r.via.lower() for r in fm3.routing_applied)
    assert not fm3.excluded_theorized


def test_level_is_carried(hydro_settings: Settings) -> None:
    comparison = hyp_stage.run_hypotheses(settings=hydro_settings, live=False)
    assert {h.hypothesis.level for h in comparison.hypotheses} == {"site"}
