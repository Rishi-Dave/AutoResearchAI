"""
Scrapy spider for efficieny large-scale scraping.
Best for:
- multiple pages
- following links
- structured data extraction
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from typing import List, Dict
import json

class ResearchSpider(scrapy.Spider):
    """
    Scrapy spider for research data collection
    Automatically handles:
    - concurrent requests
    - retries
    - rate limiting
    """

    name = 'research_spider'

    def __init__(self, urls: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls
        self.results = []

    def parse(self, response):
        """
        Parse page content
        This method is called for each scraped page
        """

        data = {
            "url": response.url,
            "title": response.css('title::text').get(),
            "headings":{
                "h1": response.css('h1::text').getall(),
                "h2": response.css('h2::text').getall(),
                "h3": response.css('h3::text').getall()
            },
            'paragraphs': response.css('p::text').getall()
        }

        all_text = ''.join(data['paragraphs'])
        data['text'] = ' '.join(all_text.split()) #removes extra whitespace

        self.results.append(data)
        yield data

class ScrapyRunner:
    #Runner class to execute Scrapy Spider programmatically

    @staticmethod
    def scrape_urls(urls:List[str]) -> List[Dict]:
        """
        Run spider on list of URLs

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scraped data dictionaries
        """
        
        results = []
        
        process = CrawlerProcess({
            "USER_AGENT": "Research Assistant Bot",
            "ROBOTSXT_OBEY": True,
            "CONURRENT_REQUESTS": 16,
            "DOWNLOAD_DELAY": 0.5
        })

        def crawler_results(signal, sender, item, response, spider):
            results.append(item)

        
        process.crawl(ResearchSpider, urls=urls)
        
        # Connect to the item_scraped signal to collect results
        for crawler in process.crawlers:
            crawler.signals.connect(crawler_results, signal=signals.item_scraped)
        
        process.start()
        return results
    
