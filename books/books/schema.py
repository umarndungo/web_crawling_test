from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import hashlib

class Book(BaseModel):
    """Pydantic model for a single book, including metadata."""
    # Core book data
    title: str
    description: Optional[str]
    category: str
    price_incl_tax: str
    price_excl_tax: str
    availability: str
    reviews: int
    image_url: str
    rating: str
    
    # Metadata
    url: str  # The source URL of the book page
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Fallback data
    raw_html: Optional[str] = None
    
    # Database ID - generated from URL hash
    id: str = Field(alias="_id")

    @classmethod
    def compute_id(cls, url: str) -> str:
        """Computes a unique SHA256 hash from the book's URL to use as a stable _id."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()