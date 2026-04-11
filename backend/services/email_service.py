# backend/services/email_service.py
# Sends formal complaint emails via SMTP using Python's built-in smtplib.
# No third-party email library is used.

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_complaint_email(
    to_email: str,
    subject: str,
    body: str,
    category: str,
    urgency: str,
) -> bool:
    """Send a formal complaint email via SMTP STARTTLS.

    The subject is automatically prefixed with category and urgency tags so
    that municipal staff can filter and prioritise incoming signals.

    Returns True on success, False on any failure (never raises).
    All errors are logged at ERROR level.
    """
    smtp_host = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    sender = os.getenv("EMAIL_SENDER", "")
    password = os.getenv("EMAIL_PASSWORD", "")

    if not sender or not password:
        logger.error(
            "Email credentials not configured. "
            "Set EMAIL_SENDER and EMAIL_PASSWORD in .env"
        )
        return False

    formatted_subject = f"[СИГНАЛ][{category}][{urgency}] Гражданска жалба"

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = formatted_subject

        # Attach body as plain UTF-8 text
        part = MIMEText(body, "plain", "utf-8")
        msg.attach(part)

        logger.info(
            "Connecting to SMTP %s:%d to send complaint to %s",
            smtp_host,
            smtp_port,
            to_email,
        )
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, [to_email], msg.as_string())

        logger.info("Email sent successfully to %s", to_email)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed. Check EMAIL_SENDER and EMAIL_PASSWORD."
        )
        return False
    except smtplib.SMTPException as exc:
        logger.error("SMTP error while sending email to %s: %s", to_email, exc)
        return False
    except OSError as exc:
        logger.error(
            "Network error connecting to SMTP %s:%d — %s", smtp_host, smtp_port, exc
        )
        return False
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Unexpected error sending email to %s: %s", to_email, exc)
        return False
