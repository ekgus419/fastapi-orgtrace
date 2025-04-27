from pydantic import BaseModel, Field

class LogoutRequestDto(BaseModel):
    username: str      = Field(..., examples=["john_doe"], description="로그아웃 아이디")
    refresh_token: str = Field(..., description="만료 되는 refresh token")
