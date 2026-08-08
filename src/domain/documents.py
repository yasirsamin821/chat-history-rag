from abc import ABC
from typing import Optional

from pydantic import UUID4, Field

from src.domain.nosql import NoSQLBaseDocument
from src.domain.types import DataCategory





class Document(NoSQLBaseDocument, ABC):
    content: dict


class CodeDocument(Document):
    name: str
    

    class Settings:
        name = DataCategory.CODE


class TextDocument(Document):
    name: str

    class Settings:
        name = DataCategory.TEXT
