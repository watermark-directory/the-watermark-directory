"""Guard: every mkdocs.yml nav target must resolve in the generated site.

The nav is hand-maintained while the corpus is reorganized by build scripts, so a
moved/renamed extraction silently breaks a nav link (mkdocs only errors on
``--strict``). This builds the site once and asserts every nav ``*.md`` target
exists under ``web/`` — covering both source-mirrored pages and generated ones.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from bosc.config import Settings
from bosc.site.build import build_site

REPO_ROOT = Path(__file__).resolve().parents[1]


class _IgnoreUnknownTags(yaml.SafeLoader):
    """mkdocs.yml carries a ``!!python/name:`` tag SafeLoader would reject."""


_IgnoreUnknownTags.add_multi_constructor(
    "tag:yaml.org,2002:python/name:", lambda loader, suffix, node: None
)


def _nav_targets(node: Any) -> list[str]:
    """Collect every leaf string value from the nested nav structure."""
    out: list[str] = []
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, list):
        for item in node:
            out.extend(_nav_targets(item))
    elif isinstance(node, dict):
        for value in node.values():
            out.extend(_nav_targets(value))
    return out


def test_every_nav_target_resolves(tmp_path: Path) -> None:
    mkdocs = yaml.load((REPO_ROOT / "mkdocs.yml").read_text(), Loader=_IgnoreUnknownTags)
    targets = [t for t in _nav_targets(mkdocs["nav"]) if t.endswith(".md")]
    assert targets, "no nav targets parsed"

    web = tmp_path / "web"
    build_site(settings=Settings(data_dir=REPO_ROOT / "data"), web_dir=web)

    missing = [t for t in targets if not (web / t).is_file()]
    assert not missing, f"nav points at pages absent from the built site: {missing}"
