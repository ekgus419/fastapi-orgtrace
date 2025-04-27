from pydantic import BaseModel, Field
from typing import Optional

class OrganizationNameAndVisibleUpdateRequestDto(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="조직명")
    is_visible: Optional[bool] = Field(None, description="표시 여부")

class OrganizationMoveRequestDto(BaseModel):
    organization_seq: int = Field(..., description="이동할 조직 ID")
    new_parent_seq: int = Field(..., description="새로운 조직 ID")