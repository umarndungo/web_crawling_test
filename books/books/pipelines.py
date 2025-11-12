import motor.motor_asyncio
from pydantic import ValidationError
from scrapy.exceptions import DropItem
from .schema import Book, ChangeLog

class MongoPipeline:
    """
    An asynchronous Scrapy pipeline for processing and storing book data.

    This pipeline connects to a MongoDB database and performs several key tasks:
    1.  Validates incoming items against the `Book` Pydantic model.
    2.  Checks if a book already exists in the database.
    3.  If the book is new, it's added to the `books` collection and a 'new'
        entry is created in the `changelog` collection.
    4.  If the book exists, it compares tracked fields (e.g., price, availability)
        for changes. Any detected changes are logged as 'update' entries in the
        `changelog` collection, and the main book record is updated.
    5.  Stores a snapshot of the raw HTML for each book in a separate `raw_html`
        collection for archival purposes.
    """
    # Define collection names for clarity and easy modification.
    BOOKS_COLLECTION = "books"
    HTML_COLLECTION = "raw_html"
    CHANGELOG_COLLECTION = "changelog"
    
    # List of fields to monitor for updates in existing books.
    FIELDS_TO_TRACK = ["price_incl_tax", "availability", "rating"]

    def __init__(self, mongo_uri, mongo_db):
        """Initializes the pipeline with MongoDB connection details."""
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        Factory method to create a pipeline instance from a Scrapy crawler.
        This method is used by Scrapy to inject settings into the pipeline.
        """
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "books_db"),
        )

    def open_spider(self, spider):
        """
        Called when the spider is opened.
        Establishes the connection to the MongoDB database.
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info("MongoDB pipeline opened and connection established.")

    def close_spider(self, spider):
        """
        Called when the spider is closed.
        Closes the connection to the MongoDB database.
        """
        self.client.close()
        spider.logger.info("MongoDB pipeline closed.")

    async def process_item(self, item, spider):
        """
        Asynchronously processes each item yielded by the spider.

        This is the core logic of the pipeline. It handles item validation,
        change detection, logging, and database persistence.

        Args:
            item: The scraped item (expected to be a `Book` object).
            spider: The spider that yielded the item.

        Returns:
            The processed item.
        """
        # Ensure we are only processing items of the correct type.
        if not isinstance(item, Book):
            return item

        try:
            # Dump the Pydantic model to a dictionary for MongoDB.
            # `by_alias=True` ensures 'id' becomes '_id'.
            item_dict = item.model_dump(by_alias=True)
            raw_html = item_dict.pop("raw_html", None)
            
            # Check if the book already exists in the database.
            existing_book = await self.db[self.BOOKS_COLLECTION].find_one({"_id": item.id})

            if not existing_book:
                # --- Handle New Books ---
                log_entry = ChangeLog(
                    book_id=item.id,
                    field_changed="book",
                    new_value=item.title,
                    change_type="new"
                )
                await self.db[self.CHANGELOG_COLLECTION].insert_one(log_entry.model_dump(by_alias=True))
                
                await self.db[self.BOOKS_COLLECTION].insert_one(item_dict)
                spider.logger.debug(f"New book found: {item.title}")

            else:
                # --- Handle Existing Books: Detect and Log Changes ---
                changes_found = []
                for field in self.FIELDS_TO_TRACK:
                    # Compare string representations to handle different types gracefully.
                    new_value = str(item_dict.get(field, ''))
                    old_value = str(existing_book.get(field, ''))
                    if old_value != new_value:
                        log_entry = ChangeLog(
                            book_id=item.id,
                            field_changed=field,
                            old_value=old_value,
                            new_value=new_value,
                            change_type="update"
                        )
                        changes_found.append(log_entry)

                if changes_found:
                    # If changes were detected, log them and update the book record.
                    await self.db[self.CHANGELOG_COLLECTION].insert_many(
                        [change.model_dump(by_alias=True) for change in changes_found]
                    )
                    await self.db[self.BOOKS_COLLECTION].update_one(
                        {"_id": item.id},
                        {"$set": item_dict}
                    )
                    spider.logger.debug(f"Updated {len(changes_found)} fields for book: {item.title}")

            # Always save/update the raw HTML snapshot.
            if raw_html:
                await self.db[self.HTML_COLLECTION].update_one(
                    {"_id": item.id},
                    {"$set": {"_id": item.id, "html": raw_html}},
                    upsert=True
                )

        except ValidationError as e:
            spider.logger.error(f"Pydantic validation error for item '{item.title}': {e}")
            raise DropItem("Item failed Pydantic validation.")
        except Exception as e:
            spider.logger.error(f"Error processing item in MongoPipeline: {e}", exc_info=True)
            raise DropItem("Unexpected error in MongoPipeline.")

        return item
