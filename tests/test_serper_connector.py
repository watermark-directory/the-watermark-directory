"""Unit tests for watermark.connectors.serper — all offline / no network."""

from __future__ import annotations

from watermark.connectors.serper import serper_search


def test_no_api_key_returns_empty() -> None:
    from watermark.config import Settings

    results = serper_search("lima ohio epa", settings=Settings(serper_api_key=""))
    assert results == []


def test_query_built_from_components(monkeypatch: object) -> None:
    """serper_search builds the right query string from keywords + domain + filetype."""
    from watermark.config import Settings

    captured: list[dict] = []

    def _fake_cached_get(connector, params, fetch, **kwargs):  # type: ignore[no-untyped-def]
        captured.append(params)
        return []

    import watermark.connectors.serper as mod

    monkeypatch.setattr(mod, "cached_get", _fake_cached_get)

    serper_search(
        "miami county",
        domain="dam.assets.ohio.gov",
        filetype="pdf",
        settings=Settings(serper_api_key="test-key"),
    )

    assert len(captured) == 1
    assert captured[0]["q"] == "miami county dam.assets.ohio.gov filetype:pdf"
    assert captured[0]["num"] == 20


def test_query_keywords_only(monkeypatch: object) -> None:
    """domain and filetype are optional — plain keyword query still works."""
    from watermark.config import Settings

    captured: list[dict] = []

    def _fake_cached_get(connector, params, fetch, **kwargs):  # type: ignore[no-untyped-def]
        captured.append(params)
        return []

    import watermark.connectors.serper as mod

    monkeypatch.setattr(mod, "cached_get", _fake_cached_get)

    serper_search("npdes permit ohio", settings=Settings(serper_api_key="test-key"))

    assert captured[0]["q"] == "npdes permit ohio"


def test_cache_ns_passed_through(monkeypatch: object) -> None:
    from watermark.config import Settings

    used_ns: list[str] = []

    def _fake_cached_get(connector, params, fetch, **kwargs):  # type: ignore[no-untyped-def]
        used_ns.append(connector)
        return []

    import watermark.connectors.serper as mod

    monkeypatch.setattr(mod, "cached_get", _fake_cached_get)

    serper_search("test", cache_ns="oepa_discovery", settings=Settings(serper_api_key="k"))
    assert used_ns == ["oepa_discovery"]
