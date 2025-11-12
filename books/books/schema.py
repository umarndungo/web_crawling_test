from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import hashlib

class Book(BaseModel):
    """
    Represents a single book scraped from the website.
    This model is used for data validation and as a structured object
    before being saved to the database.
    """
    # --- Core Book Data ---
    # Fields directly scraped from the book's page.
    title: str
    description: Optional[str]
    category: str
    price_incl_tax: str
    price_excl_tax: str
    availability: str
    reviews: int
    image_url: str
    rating: str
    
    # --- Metadata ---
    # Data added during the crawling process for tracking and reference.
    url: str  # The source URL of the book page.
    crawl_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp in UTC of when the book was crawled."
    )
    
    # --- Fallback Data ---
    # Raw data stored for recovery or re-processing purposes.
    raw_html: Optional[str] = Field(
        None,
        description="The full raw HTML of the book page, stored for archival purposes."
    )
    
    # --- Database ID ---
    # The unique identifier for the database record.
    id: str = Field(
        alias="_id",
        description="The unique ID for the book, computed from a hash of its URL."
    )

    @classmethod
    def compute_id(cls, url: str) -> str:
        """Computes a unique and stable SHA256 hash from the book's URL to use as the database _id."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()


class ChangeLog(BaseModel):
    """
    Represents a single change detected for a book during a crawl.
    Each change (e.g., a price update, a new book) is stored as one instance
    of this model in the 'changelog' collection.
    """
    book_id: str = Field(description="The ID of the book that was changed.")
    field_changed: str = Field(description="The specific field that was updated (e.g., 'price_incl_tax').")
    old_value: Optional[str] = Field(None, description="The value of the field before the change.")
    new_value: Optional[str] = Field(None, description="The value of the field after the change.")
    change_type: str = Field(description="The type of change, e.g., 'new' or 'update'.")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp in UTC of when the change was detected."
    )