# Scrapy settings for the 'books' project
#
# This file contains the most important settings for the crawler. For a full
# list of settings and their documentation, see:
# https://docs.scrapy.org/en/latest/topics/settings.html

# --- CORE PROJECT SETTINGS ---
BOT_NAME = "books"
SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"
FEED_EXPORT_ENCODING = "utf-8"

# --- ASYNC AND RESUMABILITY ---
# This reactor is required to enable support for asyncio, which is needed
# for the asynchronous 'motor' MongoDB driver used in the pipeline.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Specifies a directory where Scrapy will store the state of a crawl,
# allowing it to be paused and resumed. This is crucial for long-running crawls.
JOBDIR = "crawls/book-spider"

# --- PIPELINES AND DATABASE CONFIGURATION ---
# Defines the item pipelines that will process the scraped items.
# The number (300) determines the execution order (lower numbers run first).
ITEM_PIPELINES = {
   "books.pipelines.MongoPipeline": 300,
}
# Connection string for the MongoDB instance.
MONGO_URI = "mongodb://127.0.0.1:27017"
# The specific database to use within the MongoDB instance.
MONGO_DATABASE = "books_db"

# --- CRAWLING POLITENESS AND SPEED ---
# Respect the rules defined in the target website's robots.txt file.
ROBOTSTXT_OBEY = True

# Enable the AutoThrottle extension to automatically adjust the crawling speed
# based on the server's load. This is a best practice for being a polite crawler.
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5  # The initial download delay (in seconds).
AUTOTHROTTLE_MAX_DELAY = 60   # The maximum download delay to be set in case of high latencies.
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0 # The average number of parallel requests to send.
# AUTOTHROTTLE_DEBUG = True  # Uncomment to see throttling stats for every response.

# The number of concurrent (parallel) requests to perform per domain.
# AutoThrottle will manage the delay, but this sets an upper limit on parallelism.
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# --- ERROR HANDLING ---
# A list of HTTP status codes that should trigger a retry.
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]
# The number of times to retry a failed request.
RETRY_TIMES = 3

# --- USER AGENT ---
# It's good practice to identify your bot with a unique User-Agent string.
# USER_AGENT = "books_crawler (+http://www.your-website.com)"
