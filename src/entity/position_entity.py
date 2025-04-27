from sqlalchemy import Column, Integer, String, DateTime, func
from src.entity.base_entity import Base

class PositionEntity(Base):
    __tablename__ = "position"

    seq         = Column(Integer, primary_key=True, autoincrement=True, comment="직책 고유 순번")
    title       = Column(String(100), nullable=False,  comment="직책명 (예: CEO, CL, L, PM, M)")
    role_seq    = Column(Integer, nullable=False,      comment="직책에 할당된 역할")
    description = Column(String(255), nullable=True,   comment="직책 설명 (선택적)")
    created_at  = Column(DateTime, default=func.now(), comment="직책 생성일")
    updated_at  = Column(DateTime, default=func.now(), onupdate=func.now(), comment="직책 수정일")
    deleted_at  = Column(DateTime, nullable=True,      comment="직책 삭제일 (삭제되지 않은 경우 NULL)")
