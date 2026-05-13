import re
from playwright.async_api import async_playwright

# Keywords for Class 12
KEYWORDS_12 = [
    "senior school certificate",
    "class xii",
    "class 12",
    "12th",
    "aissce",
]



# Create two patterns to check specifically for each class
PATTERN_12 = re.compile("|".join(KEYWORDS_12), re.IGNORECASE)

async def scrape_result_links(url: str) -> list[dict]:
    found = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a mobile/standard Mac user agent helps avoid bot detection
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(url, timeout=30_000, wait_until="networkidle")

            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    href: a.href,
                    text: a.innerText.trim()
                }))
            """)

            for link in links:
                text = link.get("text", "")
                href = link.get("href", "")
                
                if not href or not text:
                    continue

                # Check for Class 12 first
                if PATTERN_12.search(text):
                    found.append({
                        "url": href, 
                        "title": f"🎓 12th: {text}"
                    })
                
                

        finally:
            await browser.close()

    return found