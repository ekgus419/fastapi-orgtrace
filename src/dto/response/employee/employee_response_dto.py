from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional

class EmployeeResponseDto(BaseModel):
    seq: int = Field(..., description="직원 순번")
    position_seq: Optional[int]     = Field(None, description="직책 순번")
    rank_seq: Optional[int]         = Field(None, description="직위 순번")
    organization_seq: Optional[int] = Field(None, description="소속 조직 순번")
    name: str                       = Field(..., description="직원 이름")
    email: EmailStr                 = Field(..., description="이메일")
    phone_number: str               = Field(..., description="핸드폰 번호")
    extension_number: str           = Field(..., description="내선 번호")
    hire_date: date                 = Field(..., description="입사일")
    birth_date: date                = Field(..., description="생년월일")
    incentive_yn: str               = Field(..., description="인센티브 여부 (Y/N)")
    marketer_yn: str                = Field(..., description="마케터 여부 (Y/N)")
    status: str                     = Field(..., description="직원 상태 코드 (100: 재직, 200: 휴직, 300: 퇴사)")
    created_at: datetime            = Field(..., description="직원 생성일")
    updated_at: datetime            = Field(..., description="직원 수정일")
    deleted_at: Optional[datetime]  = Field(None, description="퇴사일 (퇴사하지 않은 경우 NULL)")

    model_config = {
        "from_attributes": True,  # ORM 모델에서 데이터를 읽어올 때 사용
    }
