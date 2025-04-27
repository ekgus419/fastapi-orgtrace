from pydantic import BaseModel, Field
from typing import Optional

class DepartmentCreateRequestDto(BaseModel):
    """
    부문 생성 요청 DTO (level=1, parent_seq 없음)
    """
    name: str = Field(..., max_length=100, description="부문명")
    level: int = Field(1,          description="부문 (level=1)")
    parent_seq: Optional[int] = Field(None, description="상위 부문 ID")
    is_visible: bool = Field(True, description="조직 표시 여부 (TRUE: 표시, FALSE: 숨김)")

class HeadquartersCreateRequestDto(BaseModel):
    """
    본부 생성 요청 DTO (level=2, parent_seq=부문 ID 필수)
    """
    name: str = Field(..., max_length=100, description="본부명")
    level: int = Field(2,          description="본부 (level=2)")
    parent_seq: int = Field(...,   description="상위 부문 ID (필수)")
    is_visible: bool = Field(True, description="조직 표시 여부 (TRUE: 표시, FALSE: 숨김)")

class TeamCreateRequestDto(BaseModel):
    """
    팀 생성 요청 DTO (level=3, parent_seq=본부 ID 필수)
    """
    name: str = Field(..., max_length=100, description="팀명")
    level: int = Field(3,          description="팀 (level=3)")
    parent_seq: int = Field(...,   description="상위 본부 ID (필수)")
    is_visible: bool = Field(True, description="조직 표시 여부 (TRUE: 표시, FALSE: 숨김)")