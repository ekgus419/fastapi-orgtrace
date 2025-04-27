from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, func
from src.entity.base_entity import Base

class EmployeeEntity(Base):
    __tablename__ = "employee"

    seq               = Column(Integer, primary_key=True, autoincrement=True, comment="직원 고유 순번")
    position_seq      = Column(Integer, nullable=True, comment="직책 순번")
    rank_seq          = Column(Integer, nullable=True, comment="직위 순번")
    organization_seq  = Column(Integer, nullable=True, comment="소속 조직 순번")
    status            = Column(String(3), default="100", comment="직원 상태 코드 (100: 재직, 200: 휴직, 300: 퇴사)")
    name              = Column(String(100), nullable=False, comment="직원 이름")
    email             = Column(String(100), nullable=False, unique=True, comment="이메일")
    phone_number      = Column(String(20), nullable=False, comment="핸드폰 번호")
    extension_number  = Column(String(10), nullable=False, comment="내선 번호")
    hire_date         = Column(Date, nullable=False, comment="입사일")
    birth_date        = Column(Date, nullable=False, comment="생년월일")
    incentive_yn      = Column(Enum("Y", "N"), nullable=False, default="N", comment="인센티브 여부")
    marketer_yn       = Column(Enum("Y", "N"), nullable=False, default="N", comment="마케터 여부")
    created_at        = Column(DateTime, default=func.now(), comment="직원 생성일")
    updated_at        = Column(DateTime, default=func.now(), onupdate=func.now(), comment="직원 수정일")
    deleted_at        = Column(DateTime, nullable=True, comment="퇴사일 (퇴사하지 않은 경우 NULL)")
