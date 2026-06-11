import pytest

from mirad_webapp.config import load_settings


def test_load_settings_reads_provider_agnostic_email_env(monkeypatch) -> None:
    monkeypatch.setenv("EMAIL_PROVIDER", "resend")
    monkeypatch.setenv("EMAIL_FROM", "Your App <noreply@yourdomain.com>")
    monkeypatch.setenv("APP_URL", "https://yourapp.com/")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_secret")

    settings = load_settings()

    assert settings.email_provider == "resend"
    assert settings.email_from == "Your App <noreply@yourdomain.com>"
    assert settings.app_url == "https://yourapp.com"
    assert settings.resend_api_key == "re_test_secret"


def test_load_settings_rejects_invalid_app_url(monkeypatch) -> None:
    monkeypatch.setenv("APP_URL", "not-a-url")

    with pytest.raises(ValueError, match="APP_URL"):
        load_settings()


def test_load_settings_requires_https_app_url_in_production(monkeypatch) -> None:
    monkeypatch.setenv("MIRALINGO_ENV", "production")
    monkeypatch.setenv("APP_URL", "http://yourapp.com")

    with pytest.raises(ValueError, match="https"):
        load_settings()
