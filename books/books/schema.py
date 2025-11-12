from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    # pydantic schema for book items

    id: str = Field(..., alias='_id')
    availability: str
    category: str
    description: str
    image_url: str
    price_excl_tax: str
    price_incl_tax: str
    rating: str
    reviews: str
    title: str
    url: str


class ChangeLog(BaseModel):
    # Separate Collection for logging changes.

    book_url: str
    field: str
    old_value: str
    new_value: str
    timestamp: datetime = Field(
        default_factory=datetime.now
    )