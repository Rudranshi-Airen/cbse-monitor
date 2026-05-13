import smtplib, logging
from email.mime.text import MIMEText
from ws_manager import manager
from config import settings

log = logging.getLogger(__name__)

async def notify_all(link: dict):
    """Fan out to all notification channels."""
    await notify_websocket(link)
    notify_email(link)
    notify_os(link)

async def notify_websocket(link: dict):
    await manager.broadcast({
        "event": "result_found",
        "title": link["title"],
        "url": link["url"],
    })

def notify_email(link: dict):
    if not settings.notify_email:
        return
    try:
        msg = MIMEText(
            f"CBSE Class XII result link detected!\n\n"
            f"Title: {link['title']}\nURL: {link['url']}"
        )
        msg["Subject"] = "🎓 CBSE Result Alert"
        msg["From"] = settings.smtp_user
        msg["To"] = settings.notify_email

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as s:
            s.starttls()
            s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)
    except Exception as e:
        log.error(f"Email notification failed: {e}")

def notify_os(link: dict):
    """OS-level desktop notification via plyer."""
    try:
        from plyer import notification
        notification.notify(
            title="CBSE Result Alert",
            message=link["title"],
            timeout=10,
        )
    except Exception as e:
        log.warning(f"OS notification unavailable: {e}")