"""
services/sms.py — Twilio SMS integration.

Wraps the Twilio REST Client.
Returns True on success, False on any error (so the caller
can still persist the alert even when SMS delivery fails).
"""

import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from backend.config.settings import Config

logger = logging.getLogger(__name__)


def send_sms(body: str) -> bool:
    """
    Send an SMS alert via Twilio.

    Parameters
    ----------
    body : The message text (keep under 160 chars for a single SMS segment)

    Returns
    -------
    True  — Message queued by Twilio successfully
    False — Delivery failed (credentials missing, quota exceeded, etc.)
    """
    # Guard: skip if Twilio isn't configured (e.g., in dev/test)
    if not all([
        Config.TWILIO_ACCOUNT_SID,
        Config.TWILIO_AUTH_TOKEN,
        Config.TWILIO_FROM_NUMBER,
        Config.ALERT_TO_NUMBER,
    ]):
        logger.warning("Twilio not configured — SMS skipped. Body: %s", body)
        return False

    try:
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=Config.TWILIO_FROM_NUMBER,
            to=Config.ALERT_TO_NUMBER,
        )
        logger.info("📱  SMS sent — SID: %s", message.sid)
        return True

    except TwilioRestException as exc:
        logger.error("Twilio error (code %s): %s", exc.code, exc.msg)
        return False
    except Exception as exc:
        logger.error("Unexpected SMS error: %s", exc)
        return False
