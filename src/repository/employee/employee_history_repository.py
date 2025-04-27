from typing import Optional

from sqlalchemy.orm import Session

from src.domain.employee_history_domain import EmployeeHistoryDomain
from src.entity.employee_history_entity import EmployeeHistoryEntity
from src.mapper.employee_history_mapper import entity_to_domain
from src.repository.base_history_repository import BaseHistoryRepository

class EmployeeHistoryRepository(BaseHistoryRepository[EmployeeHistoryEntity]):
    """
    직원 히스토리(EmployeeHistory) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통 CRUD 기능은 BaseHistoryRepository를 상속받아 재사용하며,
    필요 시 추가 기능을 정의할 수 있음.
    """

    def __init__(self):
        """
        EmployeeHistoryRepository 생성자.
        """
        super().__init__(EmployeeHistoryEntity)

    def get_employee_history_by_seq(self, db: Session, employee_history_seq: int) -> Optional[EmployeeHistoryDomain]:
        """
        직원 히스토리 seq를 기반으로 단일 직원 히스토리 조회.

        Args:
            db (Session): 데이터베이스 세션.
            employee_history_seq (int): 조회할 직원 히스토리 seq.

        Returns:
            Optional[EmployeeHistoryDomain]: 조회된 직원 히스토리 도메인 객체 (없으면 None).
        """
        entity = self.find_by_id(db=db, entity_id=employee_history_seq)
        return entity_to_domain(entity) if entity else None