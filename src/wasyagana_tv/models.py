from datetime import datetime
from typing import Literal

from pydantic import BaseModel


THUMBNAIL_SIZE = Literal["default", "medium", "high", "standard", "maxres"]


class Channel(BaseModel):
    id: str
    title: str


class Thumbnail(BaseModel):
    size: str
    url: str
    width: int
    height: int


class Video(BaseModel):
    id: str
    title: str
    description: str
    channel: Channel
    thumbnails: dict[str, Thumbnail]
    published_at: datetime
    ordered_at: datetime
