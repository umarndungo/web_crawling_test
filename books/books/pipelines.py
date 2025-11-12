import motor.motor_asyncio
from pydantic import ValidationError
from scrapy.exceptions import DropItem
from .schema import Book

class MongoPipeline:
    """
    An asynchronous pipeline that validates Pydantic items and stores them in MongoDB.
    It saves book data to a 'books' collection and raw HTML to a 'raw_html' collection.
    """
    BOOKS_COLLECTION = "books"
    HTML_COLLECTION = "raw_html"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "books_db"),
        )

    def open_spider(self, spider):
        """Connect to MongoDB when the spider is opened."""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info("MongoDB connection opened.")

    def close_spider(self, spider):
        """Close MongoDB connection when the spider is closed."""
        self.client.close()
        spider.logger.info("MongoDB connection closed.")

    async def process_item(self, item, spider):
        """
        Process, validate, and save the item in MongoDB.
        This method is now asynchronous.
        """
        if not isinstance(item, Book):
            return item

        try:
            # The spider yields a Pydantic model directly. We dump it to a dict.
            item_dict = item.model_dump(by_alias=True)
            
            # Separate raw_html for its own collection
            raw_html = item_dict.pop("raw_html", None)

            # Upsert the main book data
            await self.db[self.BOOKS_COLLECTION].update_one(
                {"_id": item.id},
                {"$set": item_dict},
                upsert=True
            )
            
            # If raw_html exists, save it to the raw_html collection
            if raw_html:
                await self.db[self.HTML_COLLECTION].update_one(
                    {"_id": item.id},
                    {"$set": {"_id": item.id, "html": raw_html}},
                    upsert=True
                )

        except ValidationError as e:
            spider.logger.error(f"Pydantic validation error for item {item.title}: {e}")
            raise DropItem("Failed Pydantic validation")
        except Exception as e:
            spider.logger.error(f"Error processing item in MongoPipeline: {e}")
            raise DropItem(f"Pipeline error: {e}")

        return item
