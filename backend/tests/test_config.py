from app.core.config import get_settings


def test_product_lookup_defaults_use_host_only_open_facts_base_urls(monkeypatch):
    monkeypatch.delenv("PRODUCT_LOOKUP_BASE_URL", raising=False)
    monkeypatch.delenv("PRODUCT_LOOKUP_BEAUTY_BASE_URL", raising=False)
    monkeypatch.delenv("PRODUCT_LOOKUP_FOOD_BASE_URL", raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.product_lookup_beauty_base_url == "https://world.openbeautyfacts.org"
    assert settings.product_lookup_food_base_url == "https://world.openfoodfacts.org"
    assert "/api/" not in settings.product_lookup_beauty_base_url
    assert "/api/" not in settings.product_lookup_food_base_url

    get_settings.cache_clear()


def test_settings_default_to_port_8002(monkeypatch):
    monkeypatch.delenv("APP_PORT", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_port == 8002


def test_settings_allow_port_override(monkeypatch):
    monkeypatch.setenv("APP_PORT", "8015")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_port == 8015

    monkeypatch.delenv("APP_PORT", raising=False)
    get_settings.cache_clear()


def test_settings_allow_cors_allowed_origins_override(monkeypatch):
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://thatsnuts.activeadvantage.co,http://localhost:5173",
    )
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.cors_allowed_origins == [
        "https://thatsnuts.activeadvantage.co",
        "http://localhost:5173",
    ]

    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    get_settings.cache_clear()
