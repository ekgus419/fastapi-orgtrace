from typing import Tuple, List
from sqlalchemy.orm import Session
from src.dto.request.employee.employee_create_request_dto import EmployeeCreateRequestDto
from src.dto.request.employee.employee_update_request_dto import EmployeeUpdateRequestDto
from src.exception.employee_exceptions import EmployeeNotFoundException, EmployeeAlreadyExistsException, \
    EmployeeUpdateDataNotFoundException
from src.repository.employee.employee_repository import EmployeeRepository
from src.service.base_service import BaseService
from src.domain.employee_domain import EmployeeDomain
from src.decorator.transaction import Transactional  # 트랜잭션 데코레이터 추가
from src.decorator.history import History

class EmployeeService(BaseService):
    """
    직원(Employee) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근 로직은 EmployeeRepository를 통해 수행하며,
    도메인 로직을 적용하여 직원 관리 기능을 제공함.
    """

    def __init__(self, employee_repository: EmployeeRepository):
        """
        EmployeeService 생성자.

        Args:
            employee_repository (EmployeeRepository):
                직원 데이터 접근을 위한 EmployeeRepository 인스턴스.
        """
        self.employee_repository = employee_repository

    def get_employees(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str
    ) -> Tuple[List[EmployeeDomain], int]:
        """
        페이징 및 정렬을 적용하여 직원 목록을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "name").
            order (str): 정렬 방식 ("asc" 또는 "desc").

        Returns:
            Tuple[List[EmployeeDomain], int]:
                직원 도메인 리스트와 전체 직원 수.
        """
        employee_domains = self.employee_repository.get_employees(db, page, size, sort_by, order)
        total_count = self.employee_repository.count_employees(db)
        return employee_domains, total_count

    def get_employee_by_seq(self, db: Session, employee_seq: int) -> EmployeeDomain:
        """
        특정 직원 seq를 기반으로 직원 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 조회할 직원 seq.

        Returns:
            EmployeeDomain: 조회된 직원 도메인 객체.

        Raises:
            EmployeeNotFoundException: 직원이 존재하지 않을 경우.
        """
        employee_domain = self.employee_repository.get_employee_by_seq(db, employee_seq)
        if employee_domain is None:
            raise EmployeeNotFoundException()
        return employee_domain

    @Transactional
    @History(entity="employee", action="INSERT")
    def create_employee(self, db: Session, employee_create_request: EmployeeCreateRequestDto) -> EmployeeDomain:
        """
        새로운 직원을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_create_request (EmployeeCreateRequestDto): 직원 생성 요청 DTO.

        Returns:
            EmployeeDomain: 생성된 직원 도메인 객체.

        Raises:
            EmployeeAlreadyExistsException: 동일한 이메일을 가진 직원이 이미 존재하는 경우.
        """
        # 직원이 이미 존재하는지 확인
        existing_employee = self.employee_repository.get_employee_by_email(db, employee_create_request.email)
        if existing_employee:
            raise EmployeeAlreadyExistsException()

        employee_domain = EmployeeDomain(**employee_create_request.model_dump())

        return self.employee_repository.create_employee(db, employee_domain)

    @Transactional
    @History(entity="employee", action="UPDATE")
    def update_employee(self, db: Session, employee_seq: int, update_request: EmployeeUpdateRequestDto) -> EmployeeDomain:
        """
        특정 직원 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 수정할 직원 seq.
            update_request (EmployeeUpdateRequestDto): 수정할 데이터 DTO.

        Returns:
            EmployeeDomain: 수정된 직원 도메인 객체.

        Raises:
            EmployeeNotFoundException: 해당 직원이 존재하지 않을 경우.
            EmployeeUpdateDataNotFoundException: 수정할 데이터가 없을 경우.
        """
        employee_domain = self.employee_repository.get_employee_by_seq(db, employee_seq)
        if employee_domain is None:
            raise EmployeeNotFoundException()

        # DTO를 dict로 변환
        update_data = update_request.model_dump(exclude_unset=True)

        if not update_data:
            raise EmployeeUpdateDataNotFoundException()

        return self.employee_repository.update_employee(db, employee_seq, update_data)

    @Transactional
    @History(entity="employee", action="DELETE")
    def delete_employee(self, db: Session, employee_seq: int) -> bool:
        """
        특정 직원을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 삭제할 직원 seq.

        Returns:
            bool: 삭제 성공 여부.

        Raises:
            EmployeeNotFoundException: 해당 직원이 존재하지 않을 경우.
        """
        employee_domain = self.employee_repository.get_employee_by_seq(db, employee_seq)
        if employee_domain is None:
            raise EmployeeNotFoundException()

        return self.employee_repository.delete_employee(db, employee_seq)

    @Transactional
    @History(entity="employee", action="UPDATE")
    def soft_delete_employee(self, db: Session, employee_seq: int) -> EmployeeDomain:
        """
        특정 직원을 논리적으로 삭제하는 메서드 (delete_at 필드 업데이트).

        Args:
            db (Session): 데이터베이스 세션.
            employee_seq (int): 논리 삭제할 직원 seq.

        Returns:
            EmployeeDomain: 수정된 직원 도메인 객체.

        Raises:
            EmployeeNotFoundException: 해당 직원이 존재하지 않을 경우.
        """
        employee_domain = self.employee_repository.get_employee_by_seq(db, employee_seq)
        if employee_domain is None:
            raise EmployeeNotFoundException()

        return self.employee_repository.soft_delete_employee(db, employee_seq)
