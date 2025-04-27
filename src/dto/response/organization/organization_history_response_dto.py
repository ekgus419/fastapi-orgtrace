from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrganizationHistoryResponseDto(BaseModel):
    seq: int                    = Field(...,  description="조직 히스토리 고유 순번")
    organization_seq: int       = Field(...,  description="조직 고유 순번")
    action_type: str            = Field(...,  description="수정 타입")
    before_value: Optional[str] = Field(None, description="변경 전 원본 데이터")
    after_value: Optional[str]  = Field(None, description="변경 후 수정 데이터")
    username: Optional[str]     = Field(None, description="수정자")
    created_at: datetime        = Field(...,  description="조직 히스토리 생성일")

    model_config = {
        "from_attributes": True, # ORM 모델에서 데이터를 읽어올 때 사용
    }