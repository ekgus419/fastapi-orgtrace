from pydantic import BaseModel, Field
from typing import Optional

class PositionUpdateRequestDto(BaseModel):
    title: Optional[str]       = Field(None, max_length=100, description="직책명 (예: CEO, CL, L, PM, M)")
    role_seq: Optional[int]    = Field(None, description="직책에 할당된 역할")
    description: Optional[str] = Field(None, max_length=255, description="직책 설명 (선택적)")
