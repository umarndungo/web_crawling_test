from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

# NOTE: This application is designed to run with a stable Python version (e.g., Python 3.12).
# If you encountered installation issues with pydantic-core, it might be due to
# using a pre-release Python version (like 3.13) which may not be fully supported yet.
# Please ensure you are using a compatible Python environment.

app = FastAPI(
    title="FilersKeepers Book API",
    description="A RESTful API for managing book information and recent changes.",
    version="1.0.0",
)

# --- Data Models ---

class Book(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    author: str
    category: str
    price: float = Field(..., gt=0)
    rating: float = Field(..., ge=0, le=5)
    reviews: int = Field(..., ge=0)
    description: Optional[str] = None
    publication_date: Optional[datetime] = None

class Change(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    book_id: str
    change_type: str  # e.g., "price_update", "new_book", "details_update"
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)

# --- In-memory Data Storage ---
# In a real application, this would be a database (e.g., MongoDB, PostgreSQL)

books_db: List[Book] = [
    Book(
        id="b1",
        title="The Hitchhiker's Guide to the Galaxy",
        author="Douglas Adams",
        category="Science Fiction",
        price=12.99,
        rating=4.5,
        reviews=1500,
        description="A comedic science fiction series.",
        publication_date=datetime(1979, 10, 12)
    ),
    Book(
        id="b2",
        title="The Restaurant at the End of the Universe",
        author="Douglas Adams",
        category="Science Fiction",
        price=10.50,
        rating=4.2,
        reviews=1200,
        description="The second book in the Hitchhiker's Guide to the Galaxy series.",
        publication_date=datetime(1980, 9, 1)
    ),
    Book(
        id="b3",
        title="Pride and Prejudice",
        author="Jane Austen",
        category="Romance",
        price=8.75,
        rating=4.8,
        reviews=2000,
        description="A classic novel of manners.",
        publication_date=datetime(1813, 1, 28)
    ),
    Book(
        id="b4",
        title="1984",
        author="George Orwell",
        category="Dystopian",
        price=9.99,
        rating=4.7,
        reviews=1800,
        description="A dystopian social science fiction novel.",
        publication_date=datetime(1949, 6, 8)
    ),
    Book(
        id="b5",
        title="To Kill a Mockingbird",
        author="Harper Lee",
        category="Fiction",
        price=11.25,
        rating=4.9,
        reviews=2500,
        description="A novel about the serious issues of rape and racial inequality.",
        publication_date=datetime(1960, 7, 11)
    ),
    Book(
        id="b6",
        title="Dune",
        author="Frank Herbert",
        category="Science Fiction",
        price=14.99,
        rating=4.6,
        reviews=1700,
        description="A science fiction novel set in the distant future amidst a feudal interstellar society.",
        publication_date=datetime(1965, 8, 1)
    ),
    Book(
        id="b7",
        title="Foundation",
        author="Isaac Asimov",
        category="Science Fiction",
        price=13.50,
        rating=4.4,
        reviews=1300,
        description="The first novel in the Foundation series.",
        publication_date=datetime(1951, 5, 1)
    ),
    Book(
        id="b8",
        title="Sense and Sensibility",
        author="Jane Austen",
        category="Romance",
        price=7.99,
        rating=4.3,
        reviews=1100,
        description="A novel by Jane Austen, published in 1811.",
        publication_date=datetime(1811, 10, 30)
    ),
]

changes_db: List[Change] = [
    Change(book_id="b1", change_type="price_update", description="Price changed from 13.50 to 12.99"),
    Change(book_id="b3", change_type="new_book", description="Pride and Prejudice added to inventory"),
    Change(book_id="b4", change_type="details_update", description="Description updated for 1984"),
    Change(book_id="b6", change_type="new_book", description="Dune added to inventory"),
]

# --- Endpoints ---

@app.get("/books", response_model=List[Book])
async def get_books(
    category: Optional[str] = Query(None, description="Filter books by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Filter books with price greater than or equal to this value"),
    max_price: Optional[float] = Query(None, ge=0, description="Filter books with price less than or equal to this value"),
    rating: Optional[float] = Query(None, ge=0, le=5, description="Filter books with rating greater than or equal to this value"),
    sort_by: Optional[str] = Query(None, regex="^(rating|price|reviews)$", description="Sort books by 'rating', 'price', or 'reviews'"),
    skip: int = Query(0, ge=0, description="Number of items to skip (for pagination)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return (for pagination)"),
):
    """
    Retrieve a list of books with optional filtering, sorting, and pagination.
    """
    filtered_books = books_db

    if category:
        filtered_books = [book for book in filtered_books if book.category.lower() == category.lower()]
    if min_price is not None:
        filtered_books = [book for book in filtered_books if book.price >= min_price]
    if max_price is not None:
        filtered_books = [book for book in filtered_books if book.price <= max_price]
    if rating is not None:
        filtered_books = [book for book in filtered_books if book.rating >= rating]

    if sort_by:
        if sort_by == "rating":
            filtered_books.sort(key=lambda book: book.rating, reverse=True)
        elif sort_by == "price":
            filtered_books.sort(key=lambda book: book.price)
        elif sort_by == "reviews":
            filtered_books.sort(key=lambda book: book.reviews, reverse=True)

    return filtered_books[skip : skip + limit]

@app.get("/books/{book_id}", response_model=Book)
async def get_book_details(
    book_id: str = Path(..., description="The ID of the book to retrieve")
):
    """
    Retrieve full details about a specific book by its ID.
    """
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/changes", response_model=List[Change])
async def get_recent_changes():
    """
    Retrieve a list of recent updates (e.g., price changed, new book added).
    """
    # For simplicity, we return all changes. In a real app, you might
    # add pagination or time-based filtering here.
    return changes_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
