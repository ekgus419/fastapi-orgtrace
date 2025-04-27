from pydantic import BaseModel, Field
from typing import Optional

class RankUpdateRequestDto(BaseModel):
    title: str = Field(..., max_length=100, description="직위명 (예: 부문장, 본부장)")
    description: Optional[str] = Field(None, max_length=255, description="직위 설명 (선택적)")
