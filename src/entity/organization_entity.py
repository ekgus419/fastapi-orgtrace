from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from src.entity.base_entity import Base

class OrganizationEntity(Base):
    __tablename__ = "organization"

    seq        = Column(Integer,     primary_key=True, autoincrement=True, comment="조직 고유 순번")
    name       = Column(String(100), nullable=False,     comment="조직명 (부문, 본부, 팀명)")
    level      = Column(Integer,     nullable=False,     comment="조직 수준 (1: 부문, 2: 본부, 3: 팀)")
    parent_seq = Column(Integer,     nullable=True,      comment="상위 조직 순번 (부모 ID)")
    is_visible = Column(Boolean,     default=True,       comment="조직 표시 여부 (TRUE: 표시, FALSE: 숨김)")
    created_at = Column(DateTime,    default=func.now(), comment="조직 생성일")
    updated_at = Column(DateTime,    default=func.now(), onupdate=func.now(), comment="조직 수정일")
    deleted_at = Column(DateTime,    nullable=True,      comment="조직 삭제일 (삭제되지 않은 경우 NULL)")