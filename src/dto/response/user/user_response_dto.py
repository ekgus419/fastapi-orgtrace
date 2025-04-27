from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class UserResponseDto(BaseModel):
    seq: int      = Field(..., description="회원 순번")
    username: str = Field(..., description="회원 아이디")
    email: str    = Field(..., description="회원 이메일")
    type: str     = Field(..., description="회원 유형 (100: employee, 200: agency)")
    status: str   = Field(..., description="회원 상태 (100: active, 200: inactive)")
    current_refresh_token:  Optional[str] = Field(None, description="유효한 Refresh Token")
    created_at: datetime = Field(..., description="직위 생성일")
    updated_at: datetime = Field(..., description="직위 생성일")

    model_config = {
        "from_attributes": True, # ORM 모델에서 데이터를 읽어올 때 사용
    }
