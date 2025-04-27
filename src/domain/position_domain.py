from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class PositionDomain:
    title: str
    role_seq: int
    seq: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None