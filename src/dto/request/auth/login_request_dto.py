from pydantic import BaseModel, Field

class LoginRequestDto(BaseModel):
    username: str = Field(..., examples=["john_doe"], description="로그인 아이디")
    password: str = Field(..., examples=["secret123"], min_length=6, description="로그인 패스워드")
