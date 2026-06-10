"""Email helpers for password reset notifications."""

from email.message import EmailMessage
import smtplib

from fastapi import HTTPException, status

from app.core.config import settings


def validate_smtp_settings():
    """Ensure the minimum SMTP configuration is present before sending mail."""
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD or not settings.SMTP_FROM_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP configuration is missing.",
        )


def validate_smtp_login():
    """Verify that the configured SMTP credentials can authenticate."""
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    except smtplib.SMTPAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid SMTP username or app password.",
        ) from exc
    except smtplib.SMTPException as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to connect to SMTP server.",
        ) from exc


def send_reset_password_email(to_email: str, reset_link: str):
    """Send the password reset email to the requested recipient."""
    message = EmailMessage()
    message["Subject"] = "Reset Your PanditHub Password"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message.set_content(
        f"Use this link to reset your password: {reset_link}\n\n"
        f"This link expires in {settings.FORGOT_PASSWORD_EXPIRE_MINUTES} minutes."
    )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)
