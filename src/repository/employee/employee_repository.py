from typing import Optional, List
from sqlalchemy.orm import Session

from src.entity import EmployeeEntity
from src.repository.base_repository import BaseRepository
from src.mapper.employee_mapper import entity_to_domain, domain_to_entity
from src.domain.employee_domain import EmployeeDomain


class EmployeeRepository(BaseRepository[EmployeeEntity]):
    """
    직원(Employee) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통적인 CRUD 기능은 BaseRepository에서 상속받고,
    직원 관련 추가 기능을 여기에 정의함.
    """

    def __init__(self):
        """
        EmployeeRepository 생성자.
        """
        super().__init__(EmployeeEntity)

    def get_employees(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = None,
        order: str = "asc",
    ) -> List[EmployeeDomain]:
        """
        페이징 및 정렬을 적용하여 모든 직원을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str): 정렬할 컬럼명 (예: "seq", "username").
            order (str): 정렬 방식 ("asc" 또는 "desc").

        Returns:
            List[EmployeeDomain]: 조회된 직원 목록 (EmployeeDomain 객체 리스트).
        """
        employee_entities = self.find_all(db=db, page=page, size=size, sort_by=sort_by, order=order)
        return [entity_to_domain(employee) for employee in employee_entities]

    def count_employees(self, db: Session) -> int:
        """
        전체 직원 수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.

        Returns:
            int: 직원 총 개수.
        """
        return self.count_all(db=db)

    def count_employees_by_organization_seq(self, db: Session, organization_seq: int) -> int:
        """
        특정 조직에 속한 전체 직원 수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 참조할 조직 ID.

        Returns:
            int: 특정 조직에 속한 직원 총 개수.
        """
        filters = [
            self.entity.organization_seq == organization_seq,
            self.entity.deleted_at.is_(None)
        ]
        return self.count_all(filters=filters, db=db)

    def get_employee_by_seq(self, db: Session, employee_seq: int) -> Optional[EmployeeDomain]:
        """
        직원 seq를 기반으로 단일 직원을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 조회할 직원 seq.

        Returns:
            Optional[EmployeeDomain]: 조회된 EmployeeDomain 객체 (없으면 None).
        """
        entity = self.find_by_id(db=db, entity_id=employee_seq)
        return entity_to_domain(entity) if entity else None

    def get_employee_by_email(self, db: Session, email: str) -> Optional[EmployeeDomain]:
        """
        이메일을 기반으로 직원 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            email (str): 조회할 직원 이메일.

        Returns:
            Optional[EmployeeDomain]: 조회된 EmployeeDomain 객체 (없으면 None).
        """
        entity = db.query(self.entity).filter(self.entity.email == email).first()

        if entity:
            entity = db.merge(entity)
            db.refresh(entity)

        return entity_to_domain(entity) if entity else None

    def create_employee(self, db: Session, employee_domain: EmployeeDomain) -> EmployeeDomain:
        """
        새로운 직원을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_domain (EmployeeDomain): 저장할 EmployeeDomain 객체.

        Returns:
            EmployeeDomain: 저장된 EmployeeDomain 객체.
        """
        entity = domain_to_entity(employee_domain)
        saved_entity = self.save(db=db, entity=entity)
        return entity_to_domain(saved_entity)

    def update_employee(self, db: Session, employee_seq: int, update_data: dict) -> EmployeeDomain:
        """
        특정 직원 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 수정할 직원 seq.
            update_data (dict): 수정할 직원 정보.

        Returns:
            EmployeeDomain: 수정된 EmployeeDomain 객체.
        """
        updated = self.update(db=db, entity_id=employee_seq, **update_data)
        return updated

    def delete_employee(self, db: Session, employee_seq: int) -> bool:
        """
        특정 seq의 직원을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 삭제할 직원 seq.

        Returns:
            bool: 삭제 성공 여부 (True/False).
        """
        return self.delete_by_id(db=db, entity_id=employee_seq)

    def soft_delete_employee(self, db: Session, employee_seq: int) -> EmployeeDomain:
        """
        특정 seq의 직원을 논리 삭제하는 메서드.
        실제 데이터는 삭제하지 않고, delete_at 필드를 업데이트합니다.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 논리 삭제할 직원 seq.

        Returns:
            EmployeeDomain: 수정된 EmployeeDomain 객체.
        """
        return self.soft_delete_by_id(db=db, entity_id=employee_seq)
