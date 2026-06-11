import json
from contextlib import contextmanager

from mirad_webapp.config import Settings
from mirad_webapp.email_delivery import EmailDeliveryError, send_password_reset_email


@contextmanager
def _fake_response(status: int = 200):
    class Response:
        pass

    response = Response()
    response.status = status
    yield response


def test_resend_sender_posts_expected_password_reset_email(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _fake_response(200)

    monkeypatch.setattr("mirad_webapp.email_delivery.urlopen", fake_urlopen)

    result = send_password_reset_email(
        settings=Settings(
            email_provider="resend",
            email_from="Your App <noreply@yourdomain.com>",
            resend_api_key="re_test_secret",
        ),
        to_email="mira@example.com",
        reset_url="https://yourapp.com/?reset_token=raw-token",
    )

    assert result.ok is True
    assert result.provider == "resend"
    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["timeout"] == 10
    assert captured["headers"]["Authorization"] == "Bearer re_test_secret"
    assert captured["body"]["from"] == "Your App <noreply@yourdomain.com>"
    assert captured["body"]["to"] == ["mira@example.com"]
    assert "https://yourapp.com/?reset_token=raw-token" in captured["body"]["text"]
    assert "https://yourapp.com/?reset_token=raw-token" in captured["body"]["html"]


def test_resend_sender_rejects_missing_api_key() -> None:
    try:
        send_password_reset_email(
            settings=Settings(email_provider="resend", email_from="Your App <noreply@yourdomain.com>"),
            to_email="mira@example.com",
            reset_url="https://yourapp.com/?reset_token=raw-token",
        )
    except EmailDeliveryError as exc:
        assert exc.provider == "resend"
        assert exc.reason == "resend_api_key_unconfigured"
    else:
        raise AssertionError("missing Resend API key should fail before network call")
