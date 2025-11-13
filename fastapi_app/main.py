from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import re

# --- FastAPI Setup ---
app = FastAPI(
    title="FilersKeepers Book API",
    description="REST API serving scraped books data from MongoDB.",
    version="2.0.0",
)

# --- MongoDB Connection ---
MONGO_URI = "mongodb://localhost:27017"  # change if needed
client = AsyncIOMotorClient(MONGO_URI)
db = client["books_db"]
books_collection = db["books"]

# --- Rating Conversion Map ---
RATING_MAP = {
    "One": 1.0,
    "Two": 2.0,
    "Three": 3.0,
    "Four": 4.0,
    "Five": 5.0,
}

# --- Pydantic Model ---
class Book(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    availability: Optional[str] = None
    reviews: int = 0
    rating: Optional[float] = None
    image_url: Optional[str] = None
    url: Optional[str] = None
    crawl_timestamp: Optional[datetime] = None


# --- Utility Functions ---
def parse_price(price_str: Optional[str]) -> Optional[float]:
    """Convert price like '£18.02' → 18.02."""
    if not price_str:
        return None
    match = re.search(r"[\d.]+", price_str)
    return float(match.group()) if match else None


def rating_to_float(rating_str: Optional[str]) -> Optional[float]:
    """Convert text rating ('Two') → 2.0."""
    return RATING_MAP.get(rating_str.strip().title(), None) if rating_str else None


def book_from_mongo(doc: dict) -> Book:
    """Convert MongoDB document to Pydantic Book model."""
    return Book(
        id=str(doc.get("_id")),
        title=doc.get("title", "Unknown"),
        description=doc.get("description"),
        category=doc.get("category", "Default"),
        price=parse_price(doc.get("price_incl_tax")),
        availability=doc.get("availability"),
        reviews=doc.get("reviews", 0),
        rating=rating_to_float(doc.get("rating")),
        image_url=doc.get("image_url"),
        url=doc.get("url"),
        crawl_timestamp=doc.get("crawl_timestamp"),
    )

# --- API Endpoints ---

@app.get("/books", response_model=List[Book])
async def get_books(
    category: Optional[str] = Query(None, description="Filter books by category"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: Optional[str] = Query(None, regex="^(rating|price|reviews)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Retrieve books with optional filters and sorting from MongoDB.
    """
    query = {}

    # Category filter (case-insensitive)
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}

    # Price filter (parsed at runtime)
    price_conditions = {}
    if min_price is not None:
        price_conditions["$gte"] = min_price
    if max_price is not None:
        price_conditions["$lte"] = max_price
    if price_conditions:
        # We only have price as string, so we must fetch all and filter manually
        docs = books_collection.find(query)
        all_books = [book_from_mongo(doc) async for doc in docs]
        filtered_books = [
            b for b in all_books
            if b.price is not None
            and (min_price is None or b.price >= min_price)
            and (max_price is None or b.price <= max_price)
        ]
    else:
        cursor = books_collection.find(query)
        filtered_books = [book_from_mongo(doc) async for doc in cursor]

    # Filter by rating
    if rating is not None:
        filtered_books = [b for b in filtered_books if b.rating and b.rating >= rating]

    # Sort
    if sort_by:
        reverse = sort_by in ["rating", "reviews"]
        filtered_books.sort(key=lambda b: getattr(b, sort_by, 0) or 0, reverse=reverse)

    # Pagination
    return filtered_books[skip: skip + limit]


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str = Path(..., description="The MongoDB _id of the book")):
    """
    Retrieve details about a specific book by its MongoDB _id.
    """
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID format")

    doc = await books_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Book not found")

    return book_from_mongo(doc)


@app.get("/stats")
async def get_summary_stats():
    """
    Simple stats endpoint: count books, average price, etc.
    """
    count = await books_collection.count_documents({})
    sample = await books_collection.find_one()
    return {"total_books": count, "example_title": sample.get("title") if sample else None}


# --- Run the app ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
