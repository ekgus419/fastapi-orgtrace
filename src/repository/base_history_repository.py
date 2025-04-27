from src.repository.base_repository import BaseRepository
from typing import TypeVar, Generic
from sqlalchemy.orm import Session
from src.entity.base_entity import Base

T = TypeVar("T", bound=Base)

class BaseHistoryRepository(BaseRepository[T], Generic[T]):
    """
    모든 히스토리 리포지토리가 상속받는 공통 베이스 클래스.
    기본적으로 BaseRepository의 기능을 그대로 제공하며,
    필요한 경우 히스토리 전용 로직 추가 가능.
    """

    def save_history(self, db: Session, domain_obj, domain_to_entity):
        """
        도메인 객체를 받아 히스토리 엔티티로 변환 후 저장하는 메서드.

        Args:
            db (Session): 데이터베이스 트랜잭션 세션.
            domain_obj: 히스토리 도메인 객체 (예: EmployeeHistoryDomain).
            domain_to_entity (function): 도메인 객체를 엔티티로 변환하는 매퍼 함수.

        Returns:
            저장된 엔티티 객체.
        """
        entity = domain_to_entity(domain_obj)
        return self.save(db=db, entity=entity)
