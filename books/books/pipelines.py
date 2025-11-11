# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import hashlib
from . import settings
from scrapy.exceptions import DropItem
'''
class BooksPipeline:
    def process_item(self, item, spider):
        return item
'''
class MongoPipeline:
    COLLECTION_NAME ="books"

    def __init__(self, mongo_db, mongo_uri):
        # Initializes the pipeline with the MongoDB URI and database name

        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        # It gives you access to all core Scrapy components, such as the settings.
        # It creates a pipeline from a Crawler in order to make the general project settings
        # available to the pipeline.

        return cls(
            mongo_uri = crawler.settings.get("MONGO_URI"),
            mongo_db = crawler.settings.get("MONGO_DATABASE"),
        )
    
    def open_spider(self, spider):
        # It opens a connection to MongoDB when the spider starts.

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # It closes the MongoDB connection when the spider finishes.

        self.client.close()

    def process_item(self, item, spider):
        # It inserts each scraped item into the MongoDB collection.
        # It only adds unique values.
        item_id = self.compute_item_id(item)
        item_dict = ItemAdapter(item).asdict()


        self.db[self.COLLECTION_NAME].update_one(
            # A filter to find the document in the db using item_id
            filter={"_id": item_id},

            # Update the item in the db as a dictionary
            update={"$set": item_dict},

            # Only update the item if it does not exist
            upsert=True
        )

        return item

    def compute_item_id(self, item):
        # Encodes the url into a sha256 unique id
        url = item["url"]
        return hashlib.sha256(url.encode("utf-8")).hexdigest()
