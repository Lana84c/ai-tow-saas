from __future__ import annotations

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.core.config import settings


class TwilioClientError(Exception):
    pass


def get_twilio_client() -> Client:
    if not settings.TWILIO_ACCOUNT_SID:
        raise TwilioClientError("TWILIO_ACCOUNT_SID is not configured.")
    if not settings.TWILIO_AUTH_TOKEN:
        raise TwilioClientError("TWILIO_AUTH_TOKEN is not configured.")

    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_sms(to_phone: str, body: str) -> str:
    if not settings.TWILIO_PHONE_NUMBER:
        raise TwilioClientError("TWILIO_PHONE_NUMBER is not configured.")

    try:
        client = get_twilio_client()

        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone,
        )

        return message.sid

    except TwilioRestException as exc:
        raise TwilioClientError(f"Twilio send failed: {exc}") from exc
    except Exception as exc:
        raise TwilioClientError(f"Unexpected SMS error: {exc}") from exc