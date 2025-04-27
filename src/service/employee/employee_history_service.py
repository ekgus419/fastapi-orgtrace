from typing import List, Tuple
from sqlalchemy.orm import Session

from src.domain.employee_history_domain import EmployeeHistoryDomain
from src.exception.employee_history_exceptions import EmployeeHistoryNotFoundException
from src.repository.employee.employee_history_repository import EmployeeHistoryRepository
from src.entity.employee_history_entity import EmployeeHistoryEntity
from src.service.base_service import BaseService


class EmployeeHistoryService(BaseService):
    """
    직원 히스토리(EmployeeHistory) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근은 EmployeeHistoryRepository를 통해 수행하며,
    직원 히스토리 관리 기능을 제공함.
    """

    def __init__(self, employee_history_repository: EmployeeHistoryRepository):
        """
        EmployeeHistoryService 생성자.

        Args:
            employee_history_repository (EmployeeHistoryRepository):
                직원 히스토리 데이터 접근 리포지토리 인스턴스.
        """
        self.employee_history_repository = employee_history_repository

    def get_employee_histories(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str
    ) -> Tuple[List[EmployeeHistoryEntity], int]:
        """
        페이징 및 정렬을 적용하여 직원 히스토리 목록을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "name").
            order (str): 정렬 방식 ("asc" 또는 "desc").

        Returns:
            Tuple[List[EmployeeHistoryEntity], int]:
                직원 히스토리 목록과 전체 개수.

        """
        history_domains = self.employee_history_repository.find_all(db, page, size, sort_by, order)
        total_count = self.employee_history_repository.count_all(db)
        return history_domains, total_count

    def get_employee_history_by_seq(self, db: Session, employee_history_seq: int) -> EmployeeHistoryDomain:
        """
        특정 직원 히스토리 seq를 기반으로 직원 히스토리 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_history_seq (int): 조회할 직원 히스토리 seq.

        Returns:
            EmployeeHistoryDomain: 조회된 직원 히스토리 도메인 객체.

        Raises:
            EmployeeHistoryNotFoundException: 직원 히스토리가 존재하지 않을 경우.
        """
        employee_history_domain = self.employee_history_repository.get_employee_history_by_seq(db, employee_history_seq)
        if employee_history_domain is None:
            raise EmployeeHistoryNotFoundException()
        return employee_history_domain