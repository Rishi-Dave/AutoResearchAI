# test_scrapers.py

import os
import asyncio
from typing import List, Dict

# Assumes the backend directory is in your Python path.
# If not, you may need to add it, e.g., import sys; sys.path.append('..')
from backend.scrapers.search_engine import SearchEngine
from backend.scrapers.playwright_scraper import PlaywrightScraper
from backend.scrapers.scrapy_spider import ScrapyRunner

def test_search_engine():
    """Test function for SearchEngine (Step 2.1)."""
    print("\nTesting SearchEngine (Step 2.1)...")
    try:
        # NOTE: You MUST set your SERPAPI_KEY environment variable.
        # e.g., os.environ['SERPAPI_KEY'] = 'your_serpapi_key'
        search_engine = SearchEngine()
        query = "best programming language for AI"
        results = search_engine.search(query, num_results=3)

        if not results:
            print("SearchEngine test failed: No search results were returned.")
            return False

        print(f"Found {len(results)} results for query: '{query}'")
        for i, result in enumerate(results):
            print(f"--- Result {i+1} ---")
            print(f"Title: {result.get('title')}")
            print(f"Link: {result.get('link')}")
            print(f"Snippet: {result.get('snippet')[:100]}...")

        print("\nSearchEngine test passed! ✅")
        return True

    except ValueError as e:
        print(f"SearchEngine test failed: {e} ❌")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during SearchEngine test: {e} ❌")
        return False

def test_playwright_scraper():
    """Test function for PlaywrightScraper (Step 2.2)."""
    print("\nTesting PlaywrightScraper (Step 2.2)...")
    scraper = PlaywrightScraper()
    test_url = "https://www.google.com"  # A common JavaScript-heavy site

    # Using asyncio.run to execute the async scrape method
    try:
        result = scraper.scrape(test_url)

        if result.get('success'):
            print(f"Scrape successful for URL: {result.get('url')}")
            print(f"Page Title: {result.get('title')}")
            print(f"Content Length: {len(result.get('text'))} characters")
            print("\nPlaywrightScraper test passed! ✅")
            return True
        else:
            print(f"Scrape failed for URL: {result.get('url')}")
            print(f"Error: {result.get('error')}")
            print("\nPlaywrightScraper test failed. ❌")
            return False
            
    except Exception as e:
        print(f"An unexpected error occurred during PlaywrightScraper test: {e} ❌")
        return False

def test_scrapy_runner():
    """Test function for ScrapyRunner (Step 2.3)."""
    print("\nTesting ScrapyRunner (Step 2.3)...")
    runner = ScrapyRunner()
    urls = [
        "http://toscrape.com/",
        "http://quotes.toscrape.com/"
    ]
    
    try:
        results = runner.scrape_urls(urls)

        if not results:
            print("ScrapyRunner test failed: No results returned. ❌")
            return False

        print(f"Scraped {len(results)} pages successfully.")
        for result in results:
            print(f"--- Scraped Result ---")
            print(f"URL: {result.get('url')}")
            print(f"Title: {result.get('title')}")
            if 'paragraphs' in result:
                print(f"Paragraphs found: {len(result['paragraphs'])}")

        print("\nScrapyRunner test passed! ✅")
        return True
    
    except Exception as e:
        print(f"An unexpected error occurred during ScrapyRunner test: {e} ❌")
        return False

if __name__ == "__main__":
    print("Starting Module 2 Scraper Tests...")
    
    all_passed = True
    if not test_search_engine():
        all_passed = False
    
    if not test_playwright_scraper():
        all_passed = False

    if not test_scrapy_runner():
        all_passed = False

    print("\n--- Summary ---")
    if all_passed:
        print("All Module 2 tests passed successfully! 🎉")
    else:
        print("Some Module 2 tests failed. Please review the output above. 🐞")