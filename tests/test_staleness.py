"""``watermark corpus staleness`` — the reporter must never report an unknowable as fresh.

Every test here is a statement about an INVERSION. The failure mode the reporter exists to avoid
is not "it missed a stale file" — it is the #2148 shape: a check that cannot see its subject and
reports a clean one. So the assertions are mostly negative: *not* ``current``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from watermark.config import Settings
from watermark.staleness import (
    UNCHECKABLE_CADENCES,
    _git_last_commit_date,
    build_report,
    parse_prose_status_date,
)

TODAY = date(2026, 9, 16)


# --- the prose parser: the fragile half, so a miss must be unknown ---------------------------
@pytest.mark.parametrize(
    ("prose", "expected"),
    [
        # The four shapes the committed registers actually use.
        ("Status **as of 2026-08-05** (opened #1435 2026-07-10; …", date(2026, 8, 5)),
        ("Status **as of 2026-06-22**. Tags are BOSC evidentiary discipline:", date(2026, 6, 22)),
        ("corridor. Status **as of 2026-07-02; updated 2026-07-13** (#1482", date(2026, 7, 13)),
        ("Sweep status **as of 2026-07-02**; the committed-record…", date(2026, 7, 2)),
        ("#511. Base status **as of 2026-07-02**; the regulatory record", date(2026, 7, 2)),
    ],
)
def test_the_four_committed_prose_shapes_parse(prose: str, expected: date) -> None:
    """All four committed shapes, and `updated` supersedes `as of` when both appear."""
    assert parse_prose_status_date(prose) is expected or parse_prose_status_date(prose) == expected


@pytest.mark.parametrize(
    "prose",
    [
        "",
        "Status as of 2026-08-05",  # not emphasised — the shape the regex keys on is absent
        "Last swept some time in August.",
        "Status **as of soon**.",
        "Status **as of 2026-13-45**.",  # a typo is not a date
    ],
)
def test_an_unreadable_prose_date_is_none_and_never_a_guess(prose: str) -> None:
    """``None`` means UNKNOWN. The one thing the parser must never do is invent a date.

    A regex that returned ``date.today()`` on a miss — or that a caller treated as fresh — is the
    vault-inventory inversion: the gate goes quiet precisely where it cannot see.
    """
    assert parse_prose_status_date(prose) is None


def test_git_cannot_answer_outside_a_repo_and_says_so(tmp_path: Path) -> None:
    """``None``, not today. A reporter that read "git could not answer" as "fresh" would invert."""
    assert _git_last_commit_date(tmp_path / "nope.md", repo_root=tmp_path) is None


# --- the synthetic corpus: one register per standing, built from nothing ---------------------
def _mkcorpus(root: Path) -> Settings:
    """A minimal data dir with a catalog and registers, so standings can be forced one at a time."""
    (root / "extracted").mkdir(parents=True)
    (root / "catalog" / "extracted").mkdir(parents=True)
    return Settings(data_dir=root)


def _register(root: Path, slug: str, prose: str | None) -> None:
    d = root / "extracted" / slug
    d.mkdir(parents=True, exist_ok=True)
    body = f"# {slug}\n\n{prose}\n" if prose is not None else f"# {slug}\n\nno date here at all\n"
    (d / "data-centers.md").write_text(body)


def _entry(root: Path, *, eid: str, relpath: str, cadence: str, ttl: int | None = None) -> None:
    doc: dict[str, object] = {
        "id": eid,
        "title": eid,
        "scope": "extracted",
        "status": "reviewed",
        "producer": {"kind": "manual", "source": "test"},
        "storage": [{"relpath": relpath, "media_type": "text/markdown"}],
        "refresh": {"cadence": cadence, **({"ttl_days": ttl} if ttl is not None else {})},
    }
    (root / "catalog" / "extracted" / f"{eid}.yaml").write_text(yaml.safe_dump(doc))


def test_a_register_with_no_catalog_entry_is_unknown_not_fresh(tmp_path: Path) -> None:
    """Constraint 4. Five real registers are in this state and would be invisible otherwise."""
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "orphan", "Status **as of 2026-09-15**.")
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "unknown"
    assert subject.cadence is None
    assert subject in report.catalogless_registers
    assert any("NO CATALOG ENTRY" in r for r in subject.reasons)


def test_a_slug_scoped_template_entry_does_not_count_as_coverage(tmp_path: Path) -> None:
    """⚠️ The false-green this reporter was designed around.

    ``data/catalog/extracted/data-centers.yaml`` stores ``extracted/{site}/data-centers.md`` and
    so nominally matches every register. Honouring its cadence would announce full coverage over
    five registers that have no entry of their own and thirteen that share one ``last_refreshed``.
    """
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "peer", "Status **as of 2026-09-15**.")
    _entry(
        tmp_path,
        eid="data-centers",
        relpath="extracted/{site}/data-centers.md",
        cadence="weekly",
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.cadence_source == "catalog-template"
    assert subject.catalog_id == "data-centers"
    assert subject.cadence is None, "the template's cadence must NOT be adopted"
    assert subject.standing == "unknown"
    assert subject in report.catalogless_registers


def test_on_demand_is_uncheckable_and_never_current(tmp_path: Path) -> None:
    """Constraint 3. Ten real entries declare it; it must not silently mean 'never stale'."""
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "ondemand", "Status **as of 2020-01-01**.")  # ancient on purpose
    _entry(
        tmp_path,
        eid="data-centers-ondemand",
        relpath="extracted/ondemand/data-centers.md",
        cadence="on-demand",
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "uncheckable"
    assert subject.standing != "current"
    assert subject in report.uncheckable
    assert any("can never be overdue" in r for r in subject.reasons)


def test_every_uncheckable_cadence_is_a_real_catalog_cadence() -> None:
    """The set must name cadences the ``Refresh`` model actually admits, or it filters nothing."""
    from typing import get_args

    from watermark.catalog import Cadence

    assert set(get_args(Cadence)) >= UNCHECKABLE_CADENCES


def test_a_real_cadence_past_its_allowance_is_overdue(tmp_path: Path) -> None:
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "late", "Status **as of 2026-06-01**.")  # 107 days before TODAY
    _entry(
        tmp_path,
        eid="data-centers-late",
        relpath="extracted/late/data-centers.md",
        cadence="weekly",
        ttl=7,
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "overdue"
    assert subject.age_days == 107


def test_a_real_cadence_within_its_allowance_is_current(tmp_path: Path) -> None:
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "fresh", "Status **as of 2026-09-14**.")
    _entry(
        tmp_path,
        eid="data-centers-fresh",
        relpath="extracted/fresh/data-centers.md",
        cadence="weekly",
        ttl=7,
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    assert report.subjects[0].standing == "current"


def test_an_unparseable_date_with_a_real_cadence_is_unknown_not_overdue(tmp_path: Path) -> None:
    """Acceptance: "a register with an unparseable date reports unknown, not fresh."

    And not ``overdue`` either — inventing a stale verdict out of an absent date is the same
    fabrication as inventing a fresh one, just in the flattering-to-the-checker direction.
    """
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "mystery", None)
    _entry(
        tmp_path,
        eid="data-centers-mystery",
        relpath="extracted/mystery/data-centers.md",
        cadence="weekly",
        ttl=7,
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "unknown"
    assert subject.date_source == "none"
    assert subject.declared is None


def test_a_sidecar_generated_at_beats_the_prose_regex(tmp_path: Path) -> None:
    """Constraint 2: the structured date is preferred, and the report says which it used."""
    settings = _mkcorpus(tmp_path)
    _register(tmp_path, "structured", "Status **as of 2026-01-01**.")
    (tmp_path / "extracted" / "structured" / "data-centers.candidates.yaml").write_text(
        yaml.safe_dump({"generated_at": "2026-09-15", "candidates": []})
    )
    _entry(
        tmp_path,
        eid="data-centers-structured",
        relpath="extracted/structured/data-centers.md",
        cadence="weekly",
        ttl=7,
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.date_source == "sidecar"
    assert subject.declared == date(2026, 9, 15)
    assert subject.standing == "current"
    assert not any("PROSE" in r for r in subject.reasons)


# --- watches ---------------------------------------------------------------------------------
def _watch(root: Path, slug: str, name: str, doc: dict[str, object]) -> None:
    d = root / "extracted" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(yaml.safe_dump(doc))


def test_a_watch_with_no_top_level_trigger_is_unknown(tmp_path: Path) -> None:
    """Constraint 5 — build for the state where someone adds a watch and forgets.

    Four committed watches are in exactly this state today, which the brief did not expect.
    """
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "regulatory-watch.yaml",
        {"meta": {"checked_on": "2026-09-01"}, "threads": {"a": {"next_check": "2026-08-01"}}},
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.kind == "watch"
    assert subject.standing == "unknown"
    assert any("absent entirely" in r for r in subject.reasons)


def test_a_present_but_undated_trigger_reports_differently_from_an_absent_one(
    tmp_path: Path,
) -> None:
    """Both unknown, different repairs — 'annual' and '~2027-06' are present and unparseable."""
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "sdwa-watch.yaml",
        {"as_of": "2026-08-02", "next_checks": [{"date": "annual"}, {"date": "~2027-06"}]},
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "unknown"
    assert any("NO PARSEABLE DATE" in r for r in subject.reasons)
    assert not any("absent entirely" in r for r in subject.reasons)


def test_a_lapsed_trigger_is_overdue_by_its_own_promise(tmp_path: Path) -> None:
    """The independent axis: the trigger and the check are two separate declarations.

    This is the van-wert shape — a declared ``next_check`` of 2026-08-17 run thirty days late.
    The watch cannot satisfy its own trigger by restating it, which is what makes this a check
    rather than a paraphrase.
    """
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "water-watch.yaml",
        {
            "meta": {"checked_on": "2026-08-01"},
            "next_check": {"dated_triggers": [{"date": "2026-08-17", "what": "the window closes"}]},
        },
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "overdue"
    assert subject.age_days == 30
    assert any("LAPSED UNCHECKED" in r for r in subject.reasons)


def test_a_future_trigger_is_current(tmp_path: Path) -> None:
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "power-watch.yaml",
        {
            "meta": {"checked_on": "2026-09-16"},
            "next_check": {"dated_triggers": [{"date": "2026-11-03", "what": "election day"}]},
        },
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    assert report.subjects[0].standing == "current"


def test_a_trigger_due_today_is_still_open_not_lapsed(tmp_path: Path) -> None:
    """A deadline that falls today has not been blown — it is due.

    Under ``t <= today`` this reported ``current`` *and* carried a "LAPSED UNCHECKED" reason: a
    warning about a deadline still open. The standing was right by accident (age 0 against a 0-day
    allowance) and the explanation was wrong, which is the worse half.
    """
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "water-watch.yaml",
        {
            "meta": {"checked_on": "2026-09-01"},
            "next_check": {"dated_triggers": [{"date": TODAY.isoformat(), "what": "due today"}]},
        },
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "current"
    assert not any("LAPSED" in r for r in subject.reasons)
    assert any("TODAY and is still open" in r for r in subject.reasons)


def test_declared_is_always_the_watchs_own_checked_on_even_when_late(tmp_path: Path) -> None:
    """``date_source == "meta"`` must mean ``meta.checked_on`` / ``as_of`` and nothing else.

    A lapsed watch is aged from its blown TRIGGER, which is the right yardstick — but writing that
    trigger into ``declared`` made the ``--json`` output claim the file said something it did not.
    The basis is carried in ``age_from`` instead, so both facts survive.
    """
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "water-watch.yaml",
        {
            "meta": {"checked_on": "2026-08-01"},
            "next_check": {"dated_triggers": [{"date": "2026-08-17", "what": "the window closes"}]},
        },
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.declared == date(2026, 8, 1), "declared is meta.checked_on, not the trigger"
    assert subject.date_source == "meta"
    assert subject.age_from == date(2026, 8, 17), "aged from the blown trigger"
    assert subject.effective == date(2026, 8, 17)
    assert subject.age_days == 30
    assert subject.standing == "overdue"


def test_a_future_trigger_is_never_used_as_the_age_source(tmp_path: Path) -> None:
    """Only a LAPSED trigger may move the age basis; a future one must not backdate anything."""
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "power-watch.yaml",
        {
            "meta": {"checked_on": "2026-09-10"},
            "next_check": {"dated_triggers": [{"date": "2026-11-03", "what": "election day"}]},
        },
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.declared == date(2026, 9, 10)
    assert subject.age_from == date(2026, 9, 10), "the check date, NOT the 2026-11-03 trigger"
    assert subject.age_from != date(2026, 11, 3)
    assert subject.age_days == 6, "six days since the check, not negative days until the trigger"
    assert subject.standing == "current"


def test_a_watch_whose_every_trigger_is_past_and_met_is_unknown_not_current(
    tmp_path: Path,
) -> None:
    """A watch with no future trigger will never report again. That is not a clean bill of health."""
    settings = _mkcorpus(tmp_path)
    _watch(
        tmp_path,
        "peer",
        "record-watch.yaml",
        {
            "meta": {"checked_on": "2026-09-16"},
            "next_check": {"dated_triggers": [{"date": "2026-08-01", "what": "done"}]},
        },
    )
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "unknown"
    assert any("NO FUTURE TRIGGER" in r for r in subject.reasons)


def test_watches_are_discovered_in_both_committed_layouts(tmp_path: Path) -> None:
    """``<site>/*watch*.yaml`` and ``<site>/watch/*.yaml``. A hardcoded list is what goes stale."""
    settings = _mkcorpus(tmp_path)
    _watch(tmp_path, "peer", "water-watch.yaml", {"as_of": "2026-09-01"})
    nested = tmp_path / "extracted" / "peer" / "watch"
    nested.mkdir(parents=True)
    (nested / "thing.watch.yaml").write_text(yaml.safe_dump({"as_of": "2026-09-01"}))
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    assert {s.relpath for s in report.of_kind("watch")} == {
        "extracted/peer/water-watch.yaml",
        "extracted/peer/watch/thing.watch.yaml",
    }


def test_a_watch_that_does_not_parse_is_unknown_and_does_not_crash_the_report(
    tmp_path: Path,
) -> None:
    settings = _mkcorpus(tmp_path)
    d = tmp_path / "extracted" / "peer"
    d.mkdir(parents=True)
    (d / "broken-watch.yaml").write_text("next_check: [unclosed\n  - {{{\n")
    report = build_report(settings=settings, today=TODAY, repo_root=tmp_path)
    (subject,) = report.subjects
    assert subject.standing == "unknown"
    assert any("does not parse as YAML" in r for r in subject.reasons)


# --- against the live corpus: the acceptance criterion itself --------------------------------
def test_the_live_report_names_the_catalogless_registers_without_being_asked() -> None:
    """Acceptance for §B: running on a clean tree names the catalog-less registers and the
    ``on-demand`` population without a human knowing to look.

    ⚠️ Asserted as a SUBSET, not an equality. The five are the state on 2026-09-16 and the fix is a
    separate issue; when one gets an entry of its own this test must go green by *shrinking*, and an
    equality assertion would fail on the repair. What is asserted unconditionally is that the
    reporter still SEES every register — a report that silently stopped covering one is the
    inversion, and a count is what catches it.
    """
    report = build_report(today=TODAY)
    registers = report.of_kind("register")
    assert len(registers) >= 15, "every committed data-centers.md must appear"
    assert not any(s.standing == "current" for s in report.catalogless_registers)
    catalogless = {s.slug for s in report.catalogless_registers}
    assert catalogless <= {
        "bowling-green",
        "columbus",
        "findlay",
        "new-albany",
        "springfield",
    }, f"a register lost its catalog entry: {catalogless}"
    assert report.uncheckable, "the on-demand population must be named, not silently passed"
    assert all(s.cadence in UNCHECKABLE_CADENCES for s in report.uncheckable)


def test_the_live_report_never_calls_an_unknowable_subject_current() -> None:
    """The one invariant that holds whatever the corpus looks like."""
    report = build_report(today=TODAY)
    for subject in report.subjects:
        if subject.standing == "current":
            assert subject.cadence is not None
            assert subject.allowed_days is not None
            assert subject.effective is not None
