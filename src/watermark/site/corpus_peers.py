"""The yidam reports over every registered site's mirror, not only the reference build's (#2137).

The CI ``corpus`` job projects **Lima** and gates on it. Every other site's mirror was built
only when someone ran lint by hand, so a peer could regress unseen. That is how 23
`verified-unsourced` findings accumulated across four peers before #2137 measured them.

Every **registered** site is checked, not only the selectable ones. A site's mirror is
projected whether or not the site is published, and a `[verified]` claim does not become
sourced by waiting for promotion: #2137's last four uncited cells all sat on unpublished
sites (wpafb, columbus, new-albany, springfield), out of reach of a selectable-only gate.

Each site is projected into its own throwaway root, and the pinned binary reports on it. The verdicts are the binary's; this module only decides which of them fail:

* ``graph-check`` must pass, the same hard gate the reference build is held to.
* **No error-severity lint finding, on a peer.** A peer has no baseline. The one committed
  ``.yidam/lint-baseline.yml`` is keyed to the reference corpus's node paths, so for a peer it
  could only report every entry as stale. Every peer is at zero today, so zero is the ratchet.
  The reference build is exempt here because its real-root gate already covers it, with the
  baseline.
* **`verified-unsourced`, on every site including the reference.** Upstream ships it at
  ``warn``, so the binary's own gate never fails on it. It is the one check that asks whether a
  ``[verified]`` claim rests on anything, and the flattering error it guards against is
  exactly what a quiet regression looks like. The accepted gaps are enumerated in
  :data:`KNOWN_UNSOURCED`, which ratchets: a listed node that stops firing fails too, so the
  list cannot quietly come to excuse a node it no longer needs to.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from watermark.config import Settings, get_settings
from watermark.site import yidam_cli
from watermark.site.committed import site_settings
from watermark.site.corpus_mirror import regenerate_mirror
from watermark.sites import SITES, is_reference_site

VERIFIED_UNSOURCED = "verified-unsourced"

# Each entry is an accepted, still-open editorial decision. Its fix is a citation or a
# demotion, and that is the author's call, never this gate's. Keyed `<class>/<name>`, as the
# node sits under `.yidam/corpus/`. Empty since #2137 closed its last three by citation.
KNOWN_UNSOURCED: dict[str, frozenset[str]] = {}

# The files a root needs beside its mirror for the binary to read it as this repo's corpus.
_ROOT_FILES = (".yidam.toml", ".yidam/config.toml", ".yidam/authorship.yml")


@dataclass
class PeerVerdict:
    """What the binary said about one site's mirror, and which parts of it fail."""

    site: str
    graph_check: yidam_cli.Report
    lint: yidam_cli.Report
    errors: list[yidam_cli.Violation] = field(default_factory=list)
    unexpected_unsourced: list[str] = field(default_factory=list)
    stale_known: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.graph_check.passed
            and not self.errors
            and not self.unexpected_unsourced
            and not self.stale_known
        )


def _node_key(node: str) -> str:
    """``.yidam/corpus/question/lead-x.yml`` → ``question/lead-x`` (the :data:`KNOWN_UNSOURCED` key)."""
    key = node.split(":", 1)[0].removeprefix(".yidam/corpus/")
    return key.removesuffix(".yml").removesuffix(".md")


def _prepare_root(root: Path, repo_root: Path) -> Path:
    """A fresh corpus root holding the pin + vault config; returns the mirror's corpus dir."""
    if root.exists():
        shutil.rmtree(root)
    for rel in _ROOT_FILES:
        src = repo_root / rel
        if src.is_file():
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return root / ".yidam" / "corpus"


def check_site(slug: str, workdir: Path, base: Settings | None = None) -> PeerVerdict:
    """Project ``slug`` into ``<workdir>/<slug>/`` and judge the binary's reports over it."""
    base = base or get_settings()
    # Settings rejects an unknown slug, and does so before the slug becomes a path to delete.
    settings = site_settings(slug, base)
    repo_root = base.data_dir.parent
    root = workdir / slug
    corpus_dir = _prepare_root(root, repo_root)
    regenerate_mirror(settings, corpus_dir=corpus_dir, check=False)

    graph_check = yidam_cli.run_report("graph-check", root=root)
    lint = yidam_cli.run_report("lint", "--warn", root=root)
    for report in (graph_check, lint):
        # The binary resolves its root UPWARD: a workdir inside this repository is reported as
        # the repository itself, a clean and confident verdict on Lima's mirror, once per site.
        # It happened while this was written: eight "peers", all at Lima's 526 instances. The
        # root the binary names is checked rather than its lookup rule, which is upstream's.
        if report.root.resolve() != root.resolve():
            raise RuntimeError(
                f"`yidam {report.command}` reported on {report.root}, not {root} — put the "
                "workdir outside the repository"
            )
    verdict = PeerVerdict(site=slug, graph_check=graph_check, lint=lint)

    if not is_reference_site(slug):
        verdict.errors = [v for c in lint.checks if c.gates for v in c.violations]

    fired = {
        _node_key(v.node) for c in lint.checks if c.id == VERIFIED_UNSOURCED for v in c.violations
    }
    known = KNOWN_UNSOURCED.get(slug, frozenset())
    verdict.unexpected_unsourced = sorted(fired - known)
    verdict.stale_known = sorted(known - fired)
    return verdict


def check_sites(
    workdir: Path, slugs: Iterable[str] | None = None, base: Settings | None = None
) -> list[PeerVerdict]:
    """:func:`check_site` over ``slugs``, defaulting to every registered site."""
    return [check_site(slug, workdir, base) for slug in (slugs or SITES)]
