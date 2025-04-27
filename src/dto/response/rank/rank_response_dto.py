from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class RankResponseDto(BaseModel):
    seq: int   = Field(..., description="직위 순번")
    title: str = Field(..., description="직위명 (예: 부문장, 본부장)")
    description: Optional[str] = Field(None, description="직위 설명 (선택적)")
    created_at: datetime = Field(..., description="직위 생성일")
    updated_at: datetime = Field(..., description="직위 생성일")
    deleted_at: Optional[datetime] = Field(None, description="직위 삭제일 (삭제되지 않은 경우 NULL)")

    model_config = {
        "from_attributes": True, # ORM 모델에서 데이터를 읽어올 때 사용
    }
