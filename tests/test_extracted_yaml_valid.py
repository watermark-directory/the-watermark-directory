"""Every committed YAML under ``data/`` must parse.

Guards against latent syntax errors that pass ruff/mypy but break downstream
loaders — e.g. an unquoted scalar containing ``": "`` (read as a nested mapping),
or a block sequence with a trailing mapping key at the same indent. Both shipped
undetected before this test existed (the corporate-records ``subject:`` value and
the PRR-index ``minutes_corroboration`` block), because no test loaded these files.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"

_YAML_FILES = sorted(set(DATA_DIR.rglob("*.yaml")) | set(DATA_DIR.rglob("*.yml")))


def test_yaml_discovery_nonempty() -> None:
    """Sanity-check the glob actually finds the committed artifacts."""
    assert _YAML_FILES, f"no YAML files discovered under {DATA_DIR} — glob is broken"


@pytest.mark.parametrize(
    "yaml_path",
    _YAML_FILES,
    ids=[str(p.relative_to(REPO_ROOT)) for p in _YAML_FILES],
)
def test_committed_yaml_parses(yaml_path: Path) -> None:
    """Each committed YAML artifact loads without a parse error."""
    try:
        yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - failure path
        pytest.fail(f"{yaml_path.relative_to(REPO_ROOT)} is not valid YAML:\n{exc}")
