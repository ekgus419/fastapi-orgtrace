from typing import Optional

from sqlalchemy.orm import Session

from src.domain.organization_history_domain import OrganizationHistoryDomain
from src.entity.organization_history_entity import OrganizationHistoryEntity
from src.mapper.organization_history_mapper import entity_to_domain
from src.repository.base_history_repository import BaseHistoryRepository

class OrganizationHistoryRepository(BaseHistoryRepository[OrganizationHistoryEntity]):
    """
    조직 히스토리(OrganizationHistory) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통 CRUD 기능은 BaseHistoryRepository를 상속받아 재사용하며,
    필요 시 추가 기능을 정의할 수 있음.
    """

    def __init__(self):
        """
        OrganizationHistoryRepository 생성자.
        """
        super().__init__(OrganizationHistoryEntity)

    def get_organization_history_by_seq(self, db: Session, organization_history_seq: int) -> Optional[OrganizationHistoryDomain]:
        """
        조직 히스토리 seq를 기반으로 단일 조직 히스토리 조회.

        Args:
            db (Session): 데이터베이스 세션.
            organization_history_seq (int): 조회할 조직 히스토리 seq.

        Returns:
            Optional[OrganizationHistoryDomain]: 조회된 조직 히스토리 도메인 객체 (없으면 None).
        """
        entity = self.find_by_id(db=db, entity_id=organization_history_seq)
        return entity_to_domain(entity) if entity else None