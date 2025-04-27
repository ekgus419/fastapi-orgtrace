from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PositionResponseDto(BaseModel):
    seq: int      = Field(..., description="직책 순번")
    title: str    = Field(..., description="직책명 (예: CEO, CL, L, PM, M)")
    role_seq: int = Field(..., description="직책에 할당된 역할")
    description: Optional[str] = Field(None, description="직책 설명 (선택적)")
    created_at: datetime = Field(..., description="직책 생성일")
    updated_at: datetime = Field(..., description="직책 수정일")
    deleted_at: Optional[datetime] = Field(None, description="직책 삭제일 (삭제되지 않은 경우 NULL)")

    model_config = {
        "from_attributes": True, # ORM 모델에서 데이터를 읽어올 때 사용
    }
