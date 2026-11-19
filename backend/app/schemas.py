from pydantic import BaseModel
from typing import Dict, List

class DirectoryInfo(BaseModel):
    path: str
    name: str
    default: bool

class ConfigResponse(BaseModel):
    directories: List[DirectoryInfo]
    default_page_size: int

class AutocompleteItem(BaseModel):
    tag: str
    count: int

class ImageCard(BaseModel):
    id: str
    path: str
    dir: str

class SearchRequest(BaseModel):
    tags: List[str]
    directories: List[str]
    skip: int = 0
    limit: int = 50

class SearchResponse(BaseModel):
    total: int
    items: List[ImageCard]

class ImageDetail(BaseModel):
    id: str
    path: str
    filename: str
    tags: Dict[str, List[str]]
