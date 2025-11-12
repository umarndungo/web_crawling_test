from motor.motor_asyncio import AsyncIOMotorClient
from schema import Book

MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.bookstore
book_collection = database.get_collection("books")

async def connect_to_mongo():
    # A Unique index on the 'url' field
    # To prevent duplicate entries
    await book_collection.create_index("url", unique=True)