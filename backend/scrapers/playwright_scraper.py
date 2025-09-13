"""
Playwright scraper for JavaScript-heavy websites.
Playwright runs a real browser, so it can handle:
- dynamic content
- JavaScript rendering
- Complex interactions
"""

from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Optional

class PlaywrightScraper:
    """
    Scrapes websites that require JavaScript execution.
    Uses headless Chrome for efficiency
    """

    async def scrape_page(self, url: str, wait_for: Optional[str] = None):
        """
        Scraoe a single page with Playwright

        Args:
            url: Page URL
            wait_for: CSS selector to wait for (for dynamic content)
        """

        async with async_playwright() as p:
            
            browser = await p.chromium.launch(headless = True)
            page = await browser.new_page()

            try:

                await page.goto(url, wait_until="networkidle")

                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=10000)

                content = await page.content()
                title = await page.title()

                soup = BeautifulSoup(content, 'html.parser')

                for script in soup.find_all(["script", "style"]):
                    script.decompose()

                text = soup.get_text()

                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                result = {
                    "url": url,
                    "title": title,
                    "text":text,
                    "html": content,
                    "success": True
                }
            except Exception as e:
                result = {
                    "url": url,
                    "error": str(e),
                    "success": False
                }

            finally:
                await browser.close()

            return result

    def scrape(self, url: str, wait_for: Optional[str] = None):
        #Synchronous wrapper for async scrape
        return asyncio.run(self.scrape_page(url, wait_for))