from sqlalchemy import Column, Integer, String, Enum, Text, DateTime, func
from src.entity.base_entity import Base

class OrganizationHistoryEntity(Base):
    __tablename__ = "organization_history"

    seq              = Column(Integer, primary_key=True, autoincrement=True, comment="조직 히스토리 고유 순번")
    organization_seq = Column(Integer, nullable=False, comment="조직 고유 순번")
    action_type    = Column(Enum("INSERT", "UPDATE", "DELETE"), nullable=False, comment="수정 타입")
    before_value   = Column(Text, nullable=True, comment="변경 전 원본 데이터")
    after_value    = Column(Text, nullable=True, comment="변경 후 수정 데이터")
    username       = Column(String(50), nullable=True, comment="작업자")
    created_at     = Column(DateTime, default=func.now(), comment="직원 히스토리 생성일")