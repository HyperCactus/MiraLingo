"""Provider-agnostic email delivery for account recovery flows."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailDeliveryResult:
    """Sanitized delivery result safe for diagnostics."""

    ok: bool
    provider: str | None
    skipped: bool = False
    reason: str | None = None


class EmailDeliveryError(RuntimeError):
    """Raised when a configured provider cannot accept the message."""

    def __init__(self, *, provider: str, reason: str) -> None:
        super().__init__(reason)
        self.provider = provider
        self.reason = reason


def email_delivery_configured(settings: Settings) -> bool:
    """Return whether password reset email delivery is configured."""
    provider = (settings.email_provider or "").strip().lower()
    if provider == "resend":
        return bool(settings.email_from and settings.resend_api_key)
    return False


def send_password_reset_email(*, settings: Settings, to_email: str, reset_url: str) -> EmailDeliveryResult:
    """Send a password reset email using the configured provider.

    The public password-forgot endpoint intentionally does not expose this
    result because doing so could reveal whether an account exists. Callers may
    store/log the sanitized result for operator diagnostics.
    """
    provider = (settings.email_provider or "").strip().lower()
    if not provider:
        return EmailDeliveryResult(ok=False, provider=None, skipped=True, reason="email_provider_unconfigured")
    if provider == "resend":
        return _send_resend_password_reset(settings=settings, to_email=to_email, reset_url=reset_url)
    raise EmailDeliveryError(provider=provider, reason="unsupported_email_provider")


def _send_resend_password_reset(*, settings: Settings, to_email: str, reset_url: str) -> EmailDeliveryResult:
    if not settings.email_from:
        raise EmailDeliveryError(provider="resend", reason="email_from_unconfigured")
    if not settings.resend_api_key:
        raise EmailDeliveryError(provider="resend", reason="resend_api_key_unconfigured")

    payload = {
        "from": settings.email_from,
        "to": [to_email],
        "subject": "Reset your MiraLingo password",
        "html": _password_reset_html(reset_url),
        "text": _password_reset_text(reset_url),
    }
    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MiraLingo/1.0 (+https://miralingo.app)",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - fixed trusted provider URL.
            if 200 <= int(response.status) < 300:
                return EmailDeliveryResult(ok=True, provider="resend")
            raise EmailDeliveryError(provider="resend", reason=f"resend_http_{int(response.status)}")
    except HTTPError as exc:
        detail = _provider_error_detail(exc)
        if detail:
            logger.warning("Password reset email provider rejected request: provider=resend status=%s detail=%s", exc.code, detail)
        raise EmailDeliveryError(provider="resend", reason=f"resend_http_{exc.code}") from exc
    except URLError as exc:
        logger.info("Password reset email provider request failed: provider=resend reason=url_error")
        raise EmailDeliveryError(provider="resend", reason="resend_url_error") from exc
    except TimeoutError as exc:
        raise EmailDeliveryError(provider="resend", reason="resend_timeout") from exc


def _provider_error_detail(exc: HTTPError) -> str | None:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    body = body.strip()
    if not body:
        return None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body[:300]
    message = payload.get("message") if isinstance(payload, dict) else None
    name = payload.get("name") if isinstance(payload, dict) else None
    if message and name:
        return f"{name}: {message}"[:300]
    if message:
        return str(message)[:300]
    return body[:300]


def _password_reset_text(reset_url: str) -> str:
    return "\n".join(
        [
            "We received a request to reset your MiraLingo password.",
            "",
            f"Reset your password: {reset_url}",
            "",
            "If you did not request this, you can ignore this email.",
        ]
    )


def _password_reset_html(reset_url: str) -> str:
    escaped_url = reset_url.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        "<p>We received a request to reset your MiraLingo password.</p>"
        f'<p><a href="{escaped_url}">Reset your password</a></p>'
        "<p>If you did not request this, you can ignore this email.</p>"
    )
