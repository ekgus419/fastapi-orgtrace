from pydantic import BaseModel, Field

class TokenResponseDto(BaseModel):
    access_token: str = Field(...,  description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")