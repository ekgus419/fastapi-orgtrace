from src.enum.employee_enums import EmployeeStatusEnum
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class EmployeeUpdateRequestDto(BaseModel):
    position_seq: Optional[int]       = Field(None, description="직책 순번")
    rank_seq: Optional[int]           = Field(None, description="직위 순번")
    organization_seq: Optional[int]   = Field(None, description="소속 조직 순번")
    name: Optional[str]               = Field(None, max_length=100, description="직원 이름")
    email: EmailStr
    phone_number: Optional[str]       = Field(None, max_length=20, description="핸드폰 번호")
    extension_number: Optional[str]   = Field(None, max_length=10, description="내선 번호")
    hire_date: date                   = Field(default_factory=date.today, description="입사일(오늘날짜로 기본 설정)")
    birth_date: date                  = Field(default_factory=date.today, description="생일(오늘날짜로 기본 설정)")
    incentive_yn: str                 = Field("N", description="인센티브 여부 (Y/N)")
    marketer_yn: str                  = Field("Y", description="마케터 여부 (Y/N)")
    status: EmployeeStatusEnum        = Field(..., description="직원 상태 코드 (100: 재직, 200: 휴직, 300: 퇴사)")