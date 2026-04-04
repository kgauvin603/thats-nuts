from app.core.config import get_settings


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
