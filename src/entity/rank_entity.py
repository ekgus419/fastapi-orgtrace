from sqlalchemy import Column, Integer, String, DateTime, func
from src.entity.base_entity import Base

class RankEntity(Base):
    __tablename__ = "rank"

    seq = Column(Integer, primary_key=True, autoincrement=True, comment="직위 고유 순번")
    title = Column(String(100), nullable=False,       comment="직위명 (예: 부문장, 본부장)")
    description = Column(String(255), nullable=True,  comment="직위 설명 (선택적)")
    created_at = Column(DateTime, default=func.now(), comment="직위 생성일")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="직위 수정일")
    deleted_at = Column(DateTime, nullable=True,      comment="직위 삭제일 (삭제되지 않은 경우 NULL)")
