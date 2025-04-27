from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class EmployeeHistoryDomain:
    employee_seq: int
    action_type: str
    username: str
    created_at: datetime
    seq: Optional[int] = None
    before_value: Optional[str] = None
    after_value: Optional[str] = None