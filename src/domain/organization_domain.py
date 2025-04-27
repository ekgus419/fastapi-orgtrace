from dataclasses import dataclass, field
from typing import Optional,List
from datetime import datetime

@dataclass
class OrganizationDomain:
    name: str
    level: int
    is_visible: bool
    seq: Optional[int] = None
    parent_seq: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    children: List["OrganizationDomain"] = field(default_factory=list)  # 계층 구조 지원