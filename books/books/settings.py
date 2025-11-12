# Scrapy settings for books project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# --- CORE SETTINGS ---
BOT_NAME = "books"
SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

# --- ASYNC AND RESUMABILITY ---
# Enable asyncio support for asynchronous pipelines (like the one using motor)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Enable resumable crawls by persisting spider state in this directory
JOBDIR = "crawls/book-spider"

# --- PIPELINES AND DATABASE ---
ITEM_PIPELINES = {
   "books.pipelines.MongoPipeline": 300,
}
MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DATABASE = "books_db"

# --- CRAWLING POLITENESS AND SPEED ---
# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Enable AutoThrottle to dynamically adjust crawl speed based on server load
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# AUTOTHROTTLE_DEBUG = True  # Uncomment for debugging throttling issues

# The download delay and concurrent requests are now managed by AutoThrottle,
# but CONCURRENT_REQUESTS_PER_DOMAIN can be adjusted.
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# --- ERROR HANDLING ---
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]
RETRY_TIMES = 3

# --- USER AGENT ---
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "books (+http://www.yourdomain.com)"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
