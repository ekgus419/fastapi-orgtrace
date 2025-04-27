from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class OrganizationResponseDto(BaseModel):
    seq: int   = Field(..., description="조직 순번")
    name: str  = Field(..., description="조직명 (부문, 본부 팀)")
    level: int = Field(..., description="조직 수준 (1: 부문, 2: 본부, 3: 팀)")
    parent_seq: Optional[int] = Field(None, description="상위 조직 순번 (없으면 NULL)")
    is_visible: bool     = Field(..., description="조직 표시 여부 (True: 표시, False: 숨김)")
    created_at: datetime = Field(..., description="조직 생성일")
    updated_at: datetime = Field(..., description="조직 수정일")
    deleted_at: Optional[datetime] = Field(None, description="조직 삭제일 (삭제되지 않은 경우 NULL)")
    children: Optional[List["OrganizationResponseDto"]] = Field(None, description="조직 목록 (계층 구조 지원)")

    model_config = {
        "from_attributes": True,  # ORM 모델에서 데이터를 읽어올 때 사용
    }
