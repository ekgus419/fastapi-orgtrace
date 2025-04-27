from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from pydantic import EmailStr

@dataclass
class UserDomain:
    username: str
    email: EmailStr
    type: str
    status: str
    seq: Optional[int]                   = None
    password: Optional[str]              = None
    current_refresh_token: Optional[str] = None
    created_at: Optional[datetime]       = None
    updated_at: Optional[datetime]       = None
    deleted_at: Optional[datetime]       = None