"""``watermark corpus staleness`` — which registers and watches have aged out of their cadence.

**A report, never a gate.** It follows the ``mise run yidam-vendor-status`` precedent: it prints
what has drifted and exits 0 whatever it finds. Nothing in CI consumes it, and nothing should — the answer to "this
register is 86 days old" is a human deciding whether the world moved, not a failed build.

Why it exists: on 2026-09-16 five overdue watches were found and cleared, and *nothing caused that
discovery except a human asking*. Register ages that day ranged from 0 days (``lima``) to 86
(``columbus``, ``new-albany``, ``springfield``). Ten of ten data-center catalog entries declared
``refresh.cadence: on-demand`` — the one cadence that can never be overdue.

The design constraint that shapes everything here
-------------------------------------------------
**A guard that restates its subject is not a guard** (the #2069 basin-screen lesson). A reporter
that parsed the register's own "Status **as of 2026-06-22**" line and compared it to nothing would
have confirmed that the file says what it says. So every subject is measured on **three
independent axes**, each authored in a different place:

1. **declared** — the date the subject claims for itself. For a register that is its candidates
   sidecar's ``generated_at`` when one exists, and its prose line when one does not. For a watch it
   is ``meta.checked_on`` / ``as_of``.
2. **committed** — the last commit date for the path, from git. Independent of the file's *content*
   entirely, so it catches a register whose prose date was never advanced when the file was edited.
3. **expected** — the cadence, from somewhere else again: the catalog entry for a register
   (``data/catalog/<scope>/<id>.yaml``, reviewed separately), and a *dated trigger* for a watch.

A subject is ``overdue`` only when axis 3 exists and axis 1-or-2 exceeds it. Where the axes
disagree with each other that is reported too (:attr:`Subject.divergence`) — prose that has fallen
behind its own file is the failure mode that let five watches lapse.

Absence is loud, in both directions
-----------------------------------
Every unknowable is ``unknown``, never ``current``. A missing catalog entry, an unparseable prose
date, a cadence expressed as English, a watch with no top-level ``next_check`` — each reports
``unknown`` with a reason. This is the #2148 inversion written down: an inventory that cannot see
its subject must not report a clean one. ``on-demand`` and ``static`` get their own standing,
``uncheckable``, and their own section of the report, because ten entries declaring a cadence that
can never be overdue is a finding and not a pass.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from watermark.catalog import CatalogEntry, load_entries
from watermark.config import Settings, get_settings

# A cadence that can never be overdue. Declared, valid, and un-checkable — named as such rather
# than silently satisfied. `static` is a vendored snapshot; `on-demand` is a standing decision that
# the upstream does not move on a clock.
UNCHECKABLE_CADENCES = frozenset({"on-demand", "static"})

# Days a cadence allows before its subject is overdue, when the entry declares no explicit
# `ttl_days`. Deliberately generous — this is a report, and a false overdue costs a reader's
# attention, which is the only thing it has.
CADENCE_DAYS: dict[str, int] = {
    "daily": 2,
    "weekly": 10,
    "monthly": 45,
    "quarterly": 120,
    "annual": 400,
}

# A watch with an unlapsed future trigger is current until that trigger passes; there is no
# interval to compare against, so the allowance is "not yet".
_NO_LIMIT = 10**9

# How far a path's last commit may postdate the date the file claims before the report says so.
_DIVERGENCE_DAYS = 30

Standing = Literal["overdue", "current", "unknown", "uncheckable"]
Kind = Literal["register", "watch"]

# Every prose shape the committed registers actually use for their status date, e.g.
#   Status **as of 2026-08-05** (opened #1435 …
#   Status **as of 2026-06-22**. Tags are …
#   Sweep status **as of 2026-07-02**; the committed-record …
#   … **as of 2026-07-02; updated 2026-07-13** (#1482 …
# The LAST date inside the emphasised run wins, so "updated" supersedes "as of".
#
# ⚠️ This regex is the fragile half of this module and is deliberately a FALLBACK. A miss reports
# `unknown`, never fresh — but the fix is not a better regex, it is promoting the date into the
# `data-centers.candidates.yaml` sidecar's `generated_at`, which two of fifteen registers carry.
# Until the other thirteen do, `date_source == "prose"` is the report's own admission of weakness.
_PROSE_STATUS = re.compile(
    r"(?:^|\s)(?:sweep\s+|base\s+)?status\s+\*\*as\s+of\s+(?P<run>[^*]+)\*\*",
    re.IGNORECASE | re.MULTILINE,
)
_ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _iso_dates(text: str) -> list[date]:
    """Every ISO date in ``text``, in order of appearance."""
    out: list[date] = []
    for y, m, d in _ISO_DATE.findall(text):
        try:
            out.append(date(int(y), int(m), int(d)))
        except ValueError:  # 2026-13-45 and friends — a typo is not a date
            continue
    return out


def parse_prose_status_date(text: str) -> date | None:
    """The status date a register declares in prose, or ``None`` when none can be read.

    ``None`` is a first-class answer meaning **unknown**, and every caller must treat it that way:
    a register whose date cannot be read is not a fresh register.
    """
    match = _PROSE_STATUS.search(text)
    if match is None:
        return None
    dates = _iso_dates(match.group("run"))
    return dates[-1] if dates else None


def _git_last_commit_date(path: Path, *, repo_root: Path) -> date | None:
    """The author date of the last commit touching ``path``, or ``None`` if git cannot say.

    **Author date, not committer date.** A rebase rewrites committer dates wholesale, which would
    make every file in a rebased branch look freshly touched — the same trap the bundle ``updated``
    field hit. Author date survives it.

    ``None`` on any failure (not a repo, path never committed, git absent) and the caller reports
    ``unknown``. A reporter that treated "git could not answer" as "today" would invert.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    stamp = proc.stdout.strip()
    if not stamp:
        return None
    try:
        return datetime.fromisoformat(stamp).date()
    except ValueError:
        return None


class Subject(BaseModel):
    """One register or watch, reduced to its three independent dates and a standing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Kind
    slug: str  # the site slug the subject belongs to
    relpath: str  # relative to settings.data_dir
    # Axis 1 — what the subject says about itself.
    declared: date | None = None
    date_source: Literal["sidecar", "prose", "meta", "none"] = "none"
    # Axis 2 — what the repository's commit record says, independent of content.
    committed: date | None = None
    # Axis 3 — the cadence, authored elsewhere again.
    cadence: str | None = None
    cadence_source: Literal["catalog", "catalog-template", "watch-trigger", "none"] = "none"
    allowed_days: int | None = None
    catalog_id: str | None = None
    # What `age_days` was actually measured from. Normally `declared or committed`, but a watch
    # with a lapsed trigger is aged from THE TRIGGER — its own broken promise — and that date is
    # not something the file "declares" about its own freshness, so it is carried here instead of
    # being written into `declared`. Keeping them apart is what lets `date_source: "meta"` keep
    # meaning "this came from meta.checked_on / as_of" in the --json output.
    age_from: date | None = None
    # The reduction.
    standing: Standing = "unknown"
    age_days: int | None = None
    reasons: list[str] = Field(default_factory=list)
    divergence: str | None = None

    @property
    def effective(self) -> date | None:
        """The date age is measured from — an explicit basis, else the claim, else the commits."""
        return self.age_from or self.declared or self.committed


def _reduce(
    *,
    kind: Kind,
    slug: str,
    relpath: str,
    declared: date | None,
    date_source: Literal["sidecar", "prose", "meta", "none"],
    committed: date | None,
    cadence: str | None,
    cadence_source: Literal["catalog", "catalog-template", "watch-trigger", "none"],
    allowed_days: int | None,
    catalog_id: str | None,
    today: date,
    age_from: date | None = None,
    extra_reasons: list[str] | None = None,
) -> Subject:
    """Reduce three dates and a cadence to one standing. The only place a standing is decided.

    ``age_from`` overrides the date age is measured from. It exists for the one case where the
    yardstick is not the subject's own claim about itself: a watch that blew a dated trigger is
    late by the trigger, not by whenever it last said it was checked.
    """
    reasons: list[str] = list(extra_reasons or [])
    effective = age_from or declared or committed
    age = (today - effective).days if effective is not None else None

    divergence: str | None = None
    if declared is not None and committed is not None:
        drift = (committed - declared).days
        # Only a commit NEWER than the claim matters: the file moved and its stated date did not.
        #
        # ⚠️ ADVISORY, and it cannot be otherwise. This axis cannot tell a substantive revision
        # that should have advanced the status line from a typo fix that should not. 30 days is
        # chosen so the signal stays legible rather than firing on half the corpus — at 14 it
        # named 13 of 27 subjects, which is noise wearing a warning's clothes.
        if drift > _DIVERGENCE_DAYS:
            divergence = (
                f"committed {drift} days after the date it declares "
                f"({committed.isoformat()} vs {declared.isoformat()}) — a reviewed edit landed "
                "without advancing the stated date, OR the edit was cosmetic. Advisory only."
            )

    standing: Standing
    if cadence is None:
        standing = "unknown"
        reasons.append("no cadence is declared anywhere — nothing can say whether this is overdue")
    elif cadence in UNCHECKABLE_CADENCES:
        standing = "uncheckable"
        reasons.append(
            f"cadence {cadence!r} can never be overdue by construction — "
            "this is a declared decision, not a passing check"
        )
    elif allowed_days is None:
        standing = "unknown"
        reasons.append(
            f"cadence {cadence!r} is not machine-readable, so no interval can be applied"
        )
    elif effective is None:
        standing = "unknown"
        reasons.append("no date could be read from the subject or from git")
    elif age is not None and age > allowed_days:
        standing = "overdue"
        reasons.append(f"{age} days old against a {cadence} cadence ({allowed_days}-day allowance)")
    else:
        standing = "current"

    if date_source == "prose":
        reasons.append(
            "date read from PROSE by regex — fragile; promote it into the "
            "candidates sidecar's `generated_at`"
        )
    if date_source == "none" and kind == "register":
        reasons.append("no status date could be read from the register at all")

    return Subject(
        kind=kind,
        slug=slug,
        relpath=relpath,
        declared=declared,
        age_from=effective,
        date_source=date_source,
        committed=committed,
        cadence=cadence,
        cadence_source=cadence_source,
        allowed_days=allowed_days,
        catalog_id=catalog_id,
        standing=standing,
        age_days=age,
        reasons=reasons,
        divergence=divergence,
    )


def _allowed_days(entry_cadence: str, ttl_days: int | None) -> int | None:
    """The day allowance for a cadence — an explicit ``ttl_days`` wins over the default table."""
    if ttl_days is not None:
        return ttl_days
    return CADENCE_DAYS.get(entry_cadence)


class _CatalogIndex:
    """Register relpath -> the catalog entry that covers it, exact matches kept apart from templates.

    ⚠️ The distinction is the whole point. ``data/catalog/extracted/data-centers.yaml`` is
    ``slug-scoped`` and stores ``extracted/{site}/data-centers.md``, so it *nominally* covers all
    fifteen registers — which would make a catalog-driven reporter announce full coverage while
    five registers have no entry of their own and thirteen share one ``last_refreshed``. A
    template-only match therefore resolves to ``unknown``, not to the template's cadence.
    """

    def __init__(self, entries: list[CatalogEntry]) -> None:
        self.exact: dict[str, CatalogEntry] = {}
        self.templated: dict[str, CatalogEntry] = {}
        for entry in entries:
            for item in entry.storage:
                if "{site}" in item.relpath:
                    self.templated[item.relpath] = entry
                else:
                    self.exact[item.relpath] = entry

    def lookup(self, relpath: str, slug: str) -> tuple[CatalogEntry | None, bool]:
        """``(entry, is_template_only)`` for a register path."""
        exact = self.exact.get(relpath)
        if exact is not None:
            return exact, False
        for template, entry in self.templated.items():
            if template.replace("{site}", slug) == relpath:
                return entry, True
        return None, False


def _register_paths(settings: Settings) -> list[tuple[str, Path]]:
    """``(slug, path)`` for every committed data-center register, discovered not listed."""
    extracted = settings.data_dir / "extracted"
    found = sorted(extracted.glob("*/data-centers.md"))
    return [(p.parent.name, p) for p in found]


def _watch_paths(settings: Settings) -> list[tuple[str, Path]]:
    """``(slug, path)`` for every committed watch file.

    Discovered by glob across BOTH committed layouts — ``<site>/*watch*.yaml`` and
    ``<site>/watch/*.yaml`` — because the point is to catch the watch somebody adds and forgets.
    A hardcoded list is exactly what goes stale.
    """
    extracted = settings.data_dir / "extracted"
    found = set(extracted.glob("*/*watch*.yaml")) | set(extracted.glob("*/watch/*.yaml"))
    out: list[tuple[str, Path]] = []
    for path in sorted(found):
        parts = path.relative_to(extracted).parts
        out.append((parts[0], path))
    return out


def _sidecar_date(path: Path) -> date | None:
    """A register's ``generated_at`` from its candidates sidecar, when it has one."""
    sidecar = path.with_name("data-centers.candidates.yaml")
    if not sidecar.is_file():
        return None
    import yaml

    try:
        loaded = yaml.safe_load(sidecar.read_text()) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(loaded, dict):
        return None
    for key in ("generated_at", "extracted_at", "as_of"):
        raw = loaded.get(key)
        if isinstance(raw, date):
            return raw
        if isinstance(raw, str):
            dates = _iso_dates(raw)
            if dates:
                return dates[0]
    return None


def register_subjects(*, settings: Settings, today: date, repo_root: Path) -> list[Subject]:
    """Every data-center register, reduced."""
    index = _CatalogIndex(load_entries(settings=settings))
    out: list[Subject] = []
    for slug, path in _register_paths(settings):
        relpath = str(path.relative_to(settings.data_dir))
        reasons: list[str] = []

        declared = _sidecar_date(path)
        source: Literal["sidecar", "prose", "meta", "none"] = "none"
        if declared is not None:
            source = "sidecar"
        else:
            declared = parse_prose_status_date(path.read_text())
            source = "prose" if declared is not None else "none"

        entry, is_template = index.lookup(relpath, slug)
        cadence: str | None = None
        cadence_source: Literal["catalog", "catalog-template", "watch-trigger", "none"] = "none"
        allowed: int | None = None
        catalog_id: str | None = None
        if entry is None:
            reasons.append(
                "NO CATALOG ENTRY — this register is invisible to every catalog-driven check"
            )
        elif is_template:
            catalog_id = entry.id
            cadence_source = "catalog-template"
            reasons.append(
                f"covered only by the slug-scoped template entry {entry.id!r} "
                f"(last_refreshed {entry.refresh.last_refreshed!r}, shared by every site it "
                "matches) — it has no entry of its own, so its cadence is unknown"
            )
        else:
            catalog_id = entry.id
            cadence = entry.refresh.cadence
            cadence_source = "catalog"
            allowed = _allowed_days(cadence, entry.refresh.ttl_days)

        out.append(
            _reduce(
                kind="register",
                slug=slug,
                relpath=relpath,
                declared=declared,
                date_source=source,
                committed=_git_last_commit_date(path, repo_root=repo_root),
                cadence=cadence,
                cadence_source=cadence_source,
                allowed_days=allowed,
                catalog_id=catalog_id,
                today=today,
                extra_reasons=reasons,
            )
        )
    return out


def _watch_trigger_dates(doc: dict[str, object]) -> tuple[list[date], bool]:
    """Every dated trigger a watch declares at its TOP LEVEL.

    Top level only, and deliberately. ``next_check`` nested inside a thread or an
    ``instruments_to_pull`` entry is invisible to any reader who does not already know the thread
    is there — which is exactly how ``van-wert/water-watch.yaml`` ran thirty days late against a
    ``next_check`` that sat on its first pull entry. A watch that declares nothing at the top level
    declares nothing.

    Returns ``(dates, key_present)``. The flag matters: a watch with **no** ``next_check`` key and a
    watch whose ``next_checks`` say ``date: annual`` and ``date: ~2027-06`` are both un-checkable,
    but they are different repairs, and telling a reader "the key is missing" when it is present and
    unparseable sends them to the wrong line of the file.
    """
    out: list[date] = []
    present = any(k in doc for k in ("next_check", "next_checks"))
    block = doc.get("next_check")
    if isinstance(block, str):
        out.extend(_iso_dates(block))
    elif isinstance(block, dict):
        triggers = block.get("dated_triggers")
        if isinstance(triggers, list):
            for trigger in triggers:
                if isinstance(trigger, dict):
                    raw = trigger.get("date")
                    if isinstance(raw, date):
                        out.append(raw)
                    elif isinstance(raw, str):
                        out.extend(_iso_dates(raw))
        for key in ("date", "due", "on"):
            raw = block.get(key)
            if isinstance(raw, date):
                out.append(raw)
            elif isinstance(raw, str):
                out.extend(_iso_dates(raw))
    listed = doc.get("next_checks")
    if isinstance(listed, list):
        for item in listed:
            if isinstance(item, dict):
                raw = item.get("date")
                if isinstance(raw, date):
                    out.append(raw)
                elif isinstance(raw, str):
                    out.extend(_iso_dates(raw))
    return sorted(set(out)), present


def _watch_checked_on(doc: dict[str, object]) -> date | None:
    """When the watch says it was last actually run."""
    meta = doc.get("meta")
    candidates: list[object] = []
    if isinstance(meta, dict):
        candidates.extend(meta.get(k) for k in ("checked_on", "extracted_at"))
    candidates.extend(doc.get(k) for k in ("checked_on", "as_of"))
    block = doc.get("next_check")
    if isinstance(block, dict):
        candidates.append(block.get("last_actually_checked"))
    for raw in candidates:
        if isinstance(raw, date):
            return raw
        if isinstance(raw, str):
            dates = _iso_dates(raw)
            if dates:
                return dates[0]
    return None


def watch_subjects(*, settings: Settings, today: date, repo_root: Path) -> list[Subject]:
    """Every committed watch file, reduced.

    A watch's *expected* axis is a **lapsed dated trigger**: the watch named a date, and the date
    passed without ``checked_on`` reaching it. That is independent by construction — the trigger
    and the check are two separate declarations, and a watch cannot satisfy its own trigger by
    restating it.
    """
    import yaml

    out: list[Subject] = []
    for slug, path in _watch_paths(settings):
        relpath = str(path.relative_to(settings.data_dir))
        reasons: list[str] = []
        try:
            loaded = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError as exc:
            out.append(
                _reduce(
                    kind="watch",
                    slug=slug,
                    relpath=relpath,
                    declared=None,
                    date_source="none",
                    committed=_git_last_commit_date(path, repo_root=repo_root),
                    cadence=None,
                    cadence_source="none",
                    allowed_days=None,
                    catalog_id=None,
                    today=today,
                    extra_reasons=[f"the file does not parse as YAML: {exc.__class__.__name__}"],
                )
            )
            continue
        doc: dict[str, object] = loaded if isinstance(loaded, dict) else {}

        checked = _watch_checked_on(doc)
        triggers, trigger_key_present = _watch_trigger_dates(doc)
        # `t < today`, not `<=`: a trigger due TODAY has not been blown, it is due. Counting it
        # lapsed appended a "LAPSED UNCHECKED" reason to a subject the arithmetic then called
        # `current` (age 0 against a 0-day allowance) — a warning about a deadline still open.
        lapsed = [t for t in triggers if t < today and (checked is None or checked < t)]

        cadence: str | None = None
        cadence_source: Literal["catalog", "catalog-template", "watch-trigger", "none"] = "none"
        allowed: int | None = None
        # `declared` stays the watch's own `meta.checked_on` / `as_of` in every branch below. Only
        # the AGE BASIS moves, and only for a lapsed trigger.
        age_basis: date | None = None

        if not triggers:
            reasons.append(
                "TOP-LEVEL `next_check` / `next_checks` DECLARES NO PARSEABLE DATE — it is present "
                "but carries only prose (a cadence in English, or a date like 'annual' / '~2027-06')"
                if trigger_key_present
                else "NO TOP-LEVEL DATED TRIGGER — `next_check` / `next_checks` is absent entirely, "
                "or sits nested inside a thread where no reader will find it"
            )
        elif lapsed:
            # Age is measured from the LAPSED TRIGGER, not from the check: the watch's own promise
            # is the yardstick, and a zero allowance makes any lapse overdue by exactly its lateness.
            oldest = min(lapsed)
            cadence, cadence_source, allowed = "dated-trigger", "watch-trigger", 0
            age_basis = oldest
            reasons.append(
                f"trigger {oldest.isoformat()} LAPSED UNCHECKED — "
                f"last actually checked {checked.isoformat() if checked else 'never stated'}"
            )
        else:
            # Due today counts as live: the deadline has not passed.
            live = [t for t in triggers if t >= today]
            if live:
                cadence, cadence_source = "dated-trigger", "watch-trigger"
                allowed = _NO_LIMIT  # a live trigger exists and has not passed
                nxt = min(live)
                reasons.append(
                    "a dated trigger falls TODAY and is still open"
                    if nxt == today
                    else f"next dated trigger {nxt.isoformat()}"
                )
            else:
                # Every trigger is past and each was met. Nothing is overdue — and nothing ever
                # will be, because there is no future trigger left to lapse. That is `unknown`.
                reasons.append(
                    "every dated trigger is in the past and each was checked in time, but there "
                    "is NO FUTURE TRIGGER — add one or this watch will never report again"
                )

        out.append(
            _reduce(
                kind="watch",
                slug=slug,
                relpath=relpath,
                declared=checked,
                date_source="meta" if checked is not None else "none",
                age_from=age_basis,
                committed=_git_last_commit_date(path, repo_root=repo_root),
                cadence=cadence,
                cadence_source=cadence_source,
                allowed_days=allowed,
                catalog_id=None,
                today=today,
                extra_reasons=reasons,
            )
        )
    return out


class StalenessReport(BaseModel):
    """The whole report — every subject, plus the rollups the reader actually reads."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    asof: date
    subjects: list[Subject]

    def of_kind(self, kind: Kind) -> list[Subject]:
        return [s for s in self.subjects if s.kind == kind]

    def with_standing(self, standing: Standing) -> list[Subject]:
        return [s for s in self.subjects if s.standing == standing]

    @property
    def catalogless_registers(self) -> list[Subject]:
        """Registers no catalog entry of their own covers — template-only included."""
        return [
            s
            for s in self.subjects
            if s.kind == "register" and s.cadence_source in {"none", "catalog-template"}
        ]

    @property
    def uncheckable(self) -> list[Subject]:
        """Subjects whose declared cadence can never be overdue. Named, never counted as passing."""
        return self.with_standing("uncheckable")

    @property
    def divergent(self) -> list[Subject]:
        return [s for s in self.subjects if s.divergence is not None]


def build_report(
    *,
    settings: Settings | None = None,
    today: date | None = None,
    repo_root: Path | None = None,
) -> StalenessReport:
    """Measure every register and watch. Pure read — writes nothing, exits nobody."""
    settings = settings or get_settings()
    today = today or date.today()
    repo_root = repo_root or settings.data_dir.parent
    subjects = register_subjects(settings=settings, today=today, repo_root=repo_root)
    subjects += watch_subjects(settings=settings, today=today, repo_root=repo_root)
    return StalenessReport(asof=today, subjects=subjects)
