BOT_NAME = "komkom_scraper"

SPIDER_MODULES = ["komkom_scraper.spiders"]
NEWSPIDER_MODULE = "komkom_scraper.spiders"

DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 8

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    # Add more user-agents as needed
]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'komkom_scraper.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
}

ITEM_PIPELINES = {
    "komkom_scraper.pipelines.NormalizationPipeline": 100,
    "komkom_scraper.pipelines.PostgresPipeline": 200,
}

RETRY_ENABLED = True
RETRY_TIMES = 3

LOG_LEVEL = "INFO"

# Custom middleware for user-agent rotation
import random
from scrapy import signals

class RandomUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agents=crawler.settings.get('USER_AGENTS', [])
        )

    def process_request(self, request, spider):
        if self.user_agents:
            request.headers.setdefault('User-Agent', random.choice(self.user_agents))