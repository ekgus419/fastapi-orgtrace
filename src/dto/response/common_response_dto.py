from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar

DataT = TypeVar("DataT")

class CommonResponseDto(BaseModel, Generic[DataT]):
    status: str            = Field(...,  description="공통 응답 상태 (success, error, fail)")
    data: Optional[DataT]  = Field(None, description="공통 응답 데이터")
    message: Optional[str] = Field(None, description="공통 응답 메시지")
