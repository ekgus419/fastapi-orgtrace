from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class EmployeeDomain:
    status: str
    name: str
    email: str
    phone_number: str
    extension_number: str
    hire_date: date
    birth_date: date
    incentive_yn: str
    marketer_yn: str
    seq: Optional[int]              = None
    position_seq: Optional[int]     = None
    rank_seq: Optional[int]         = None
    organization_seq: Optional[int] = None
    created_at: Optional[datetime]  = None
    updated_at: Optional[datetime]  = None
    deleted_at: Optional[datetime]  = None
