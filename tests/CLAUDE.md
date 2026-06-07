# CLAUDE.md — `tests`

Offline test suite. Defers to the root [`CLAUDE.md`](../CLAUDE.md).

- **Tests are hermetic — no network.** Hydrology/connector tests use the
  `hydro_settings` fixture in `conftest.py` (`hydro_offline=True`,
  `hydro_fixtures_dir` → [`tests/fixtures/hydrology/`](fixtures/README.md)). Inject
  that `Settings` rather than fighting `get_settings()`'s `lru_cache`.
- Tests run against **committed `data/extracted/**`** (the reviewed artifact) and
  committed fixtures — not against raw `data/documents/**` and not the live API.
- A new connector code path needs a committed fixture; an offline cache miss raises
  `HydroOfflineError` naming the key to record. Keep fixtures minimal; don't
  hand-edit recorded JSON.
- `test_extracted_yaml_valid.py` validates every committed extraction against
  `bosc.models` — adding extractions to the corpus means they must stay schema-valid.
- Run via `mise run check` (ruff + mypy strict + pytest) before declaring done.
