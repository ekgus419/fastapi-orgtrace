from typing import List, Tuple
from sqlalchemy.orm import Session

from src.domain.organization_history_domain import OrganizationHistoryDomain
from src.exception.organization_history_exceptions import OrganizationHistoryNotFoundException
from src.repository.organization.organization_history_repository import OrganizationHistoryRepository
from src.entity.organization_history_entity import OrganizationHistoryEntity
from src.service.base_service import BaseService


class OrganizationHistoryService(BaseService):
    """
    조직 히스토리(OrganizationHistory) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근은 OrganizationHistoryRepository를 통해 수행하며,
    조직 히스토리 관리 기능을 제공함.
    """

    def __init__(self, organization_history_repository: OrganizationHistoryRepository):
        """
        OrganizationHistoryService 생성자.

        Args:
            organization_history_repository (OrganizationHistoryRepository):
                조직 히스토리 데이터 접근 리포지토리 인스턴스.
        """
        self.organization_history_repository = organization_history_repository

    def get_organization_histories(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str
    ) -> Tuple[List[OrganizationHistoryEntity], int]:
        """
        페이징 및 정렬을 적용하여 조직 히스토리 목록을 조회하는 메서드.

        Args:
            db (Session): SQLAlchemy 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "name").
            order (str): 정렬 방식 ("asc" 또는 "desc").

        Returns:
            Tuple[List[OrganizationHistoryEntity], int]:
                조직 히스토리 리스트와 전체 조직 히스토리 개수.
        """
        history_domains = self.organization_history_repository.find_all(db, page, size, sort_by, order)
        total_count = self.organization_history_repository.count_all(db)
        return history_domains, total_count

    def get_organization_history_by_seq(self, db: Session, organization_history_seq: int) -> OrganizationHistoryDomain:
        """
        특정 조직 히스토리 seq를 기반으로 조직 히스토리 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_history_seq (int): 조회할 조직 히스토리 seq.

        Returns:
            OrganizationHistoryDomain: 조회된 조직 히스토리 도메인 객체.

        Raises:
            OrganizationHistoryNotFoundException: 조직 히스토리 정보가 존재하지 않을 경우.
        """
        organization_history_domain = self.organization_history_repository.get_organization_history_by_seq(db, organization_history_seq)
        if organization_history_domain is None:
            raise OrganizationHistoryNotFoundException()
        return organization_history_domain