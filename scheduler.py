import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import scrape_result_links
from state import is_new_link, save_link
from notifier import notify_all
from config import settings

log = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def poll_cbse():
    log.info(f"Polling {settings.target_url} ...")
    try:
        links = await scrape_result_links(settings.target_url)
        for link in links:
            if is_new_link(link["url"]):
                log.info(f"NEW RESULT LINK DETECTED: {link['title']}")
                save_link(link["url"], link["title"])
                await notify_all(link)
    except Exception as e:
        log.error(f"Poll failed: {e}")

def start_scheduler():
    scheduler.add_job(
        poll_cbse,
        trigger="interval",
        seconds=settings.poll_interval_seconds,
        id="cbse_poll",
        replace_existing=True,
    )
    scheduler.start()
    log.info("Scheduler started — polling every 5 minutes.")