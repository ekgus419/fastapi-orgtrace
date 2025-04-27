from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginatedResponseDto(BaseModel, Generic[T]):
    items: List[T] = Field(...,   description="아이템 목록")
    total: int = Field(...,       description="전체 아이템 수")
    page: int = Field(...,        description="현재 페이지 (1-based)")
    size: int = Field(...,        description="한 페이지당 아이템 수")
    total_pages: int = Field(..., description="전체 페이지 수")
