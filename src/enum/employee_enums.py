from enum import Enum

class EmployeeStatusEnum(str, Enum):
    ACTIVE  = "100"   # 재직
    LEAVE   = "200"   # 휴직
    RETIRED = "300"   # 퇴사
