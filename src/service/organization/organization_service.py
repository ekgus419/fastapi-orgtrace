from typing import Tuple, List, Optional
from sqlalchemy.orm import Session

from src.decorator.history import History
from src.decorator.transaction import Transactional  # 트랜잭션 데코레이터 추가
from src.domain.organization_domain import OrganizationDomain
from src.dto.request.organization.organization_create_request_dto import TeamCreateRequestDto, \
    HeadquartersCreateRequestDto, DepartmentCreateRequestDto
from src.dto.request.organization.organization_update_request_dto import OrganizationNameAndVisibleUpdateRequestDto, \
    OrganizationMoveRequestDto
from src.exception.organization_exceptions import OrganizationNotFoundException, SubOrganizationsExistException, \
    InvalidDivisionParentException, MissingParentForHeadquarterException, InvalidDivisionIdException, \
    MissingParentForTeamException, InvalidHeadquarterIdException, InvalidOrganizationLevelException, \
    EmployeesExistInOrganizationException, OrganizationUpdateDataNotFoundException
from src.repository.employee.employee_repository import EmployeeRepository
from src.repository.organization.organization_repository import OrganizationRepository
from src.service.base_service import BaseService


class OrganizationService(BaseService):
    """
    조직(Organization) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근 로직은 OrganizationRepository를 통해 수행하며,
    도메인 로직을 적용하여 조직 관리 기능을 제공함.
    """

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        employee_repository: EmployeeRepository
    ):
        """
        OrganizationService 생성자.

        Args:
            organization_repository (OrganizationRepository):
                조직 데이터 접근을 위한 OrganizationRepository 인스턴스.
            employee_repository (EmployeeRepository):
                직원 데이터 접근을 위한 EmployeeRepository 인스턴스.
        """
        self.organization_repository = organization_repository
        self.employee_repository = employee_repository

    def get_organizations(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str,
        level: Optional[int],
        parent_seq: Optional[int]
    ) -> Tuple[List[OrganizationDomain], int]:
        """
        페이징 및 정렬을 적용하여 조직 목록을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지당 데이터 수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "name").
            order (str): 정렬 방식 ("asc" | "desc").
            level (Optional[int]): 조직 level (1: 부문, 2: 본부, 3: 팀).
            parent_seq (Optional[int]): 상위 조직 seq.

        Returns:
            Tuple[List[OrganizationDomain], int]:
                조직 도메인 리스트와 전체 조직 수.
        """
        filters = []
        if level is not None:
            filters.append(self.organization_repository.entity.level == level)
        if parent_seq is not None:
            filters.append(self.organization_repository.entity.parent_seq == parent_seq)

        organization_domains = self.organization_repository.get_organizations(db, page, size, sort_by, order, filters)
        total_count = self.organization_repository.count_organizations(db, filters)
        return organization_domains, total_count

    def get_organization_by_seq(self, db: Session, organization_seq: int) -> OrganizationDomain:
        """
        특정 조직 seq를 기반으로 조직 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 조회할 조직 seq.

        Returns:
            OrganizationDomain: 조회된 조직 도메인 객체.

        Raises:
            OrganizationNotFoundException: 조직이 존재하지 않을 경우.
        """
        organization_domain = self.organization_repository.get_organization_by_seq(db, organization_seq)
        if organization_domain is None:
            raise OrganizationNotFoundException()
        return organization_domain

    @Transactional
    @History(entity="organization", action="INSERT")
    def create_department(self, db: Session, department_create_request_dto: DepartmentCreateRequestDto) -> OrganizationDomain:
        """
        새로운 부문을 생성하는 메서드(level=1).
        - `parent_seq`는 항상 `None`

        Args:
            db (Session): 데이터베이스 세션.
            department_create_request_dto (DepartmentCreateRequestDto): 부문 생성 요청 DTO.

        Returns:
            OrganizationDomain: 생성된 조직(부문) 도메인 객체.

        Raises:
            InvalidOrganizationLevelException: level이 1이 아닌 경우.
            InvalidDivisionParentException: parent_seq가 있는 경우.
        """
        if department_create_request_dto.level != 1:
            raise InvalidOrganizationLevelException()

        if department_create_request_dto.parent_seq is not None:
            raise InvalidDivisionParentException()

        department_domain = OrganizationDomain(**department_create_request_dto.model_dump())

        return self.organization_repository.create_organization(db=db, organization_domain=department_domain)

    @Transactional
    @History(entity="organization", action="INSERT")
    def create_headquarters(self, db: Session, headquarters_create_request_dto: HeadquartersCreateRequestDto) -> OrganizationDomain:
        """
        새로운 본부를 생성하는 메서드(level=2).
        - 반드시 `parent_seq`(부문 ID)가 존재해야 함

        Args:
            db (Session): 데이터베이스 세션.
            headquarters_create_request_dto (HeadquartersCreateRequestDto): 본부 생성 요청 DTO.

        Returns:
            OrganizationDomain: 생성된 조직(본부) 도메인 객체.

        Raises:
            InvalidOrganizationLevelException: level이 2가 아닌 경우.
            MissingParentForHeadquarterException: parent_seq가 없는 경우.
            InvalidDivisionIdException: 상위 부문이 유효하지 않은 경우.
        """
        if headquarters_create_request_dto.level != 2:
            raise InvalidOrganizationLevelException()

        if headquarters_create_request_dto.parent_seq is None:
            raise MissingParentForHeadquarterException()

        existing_department = self.organization_repository.get_organization_by_seq(db, headquarters_create_request_dto.parent_seq)
        if not existing_department or existing_department.level != 1:
            raise InvalidDivisionIdException()

        headquarters_domain = OrganizationDomain(**headquarters_create_request_dto.model_dump())

        return self.organization_repository.create_organization(db=db, organization_domain=headquarters_domain)

    @Transactional
    @History(entity="organization", action="INSERT")
    def create_team(self, db: Session, team_create_request_dto: TeamCreateRequestDto) -> OrganizationDomain:
        """
        새로운 팀을 생성하는 메서드(level=3).
        - 반드시 `parent_seq`(본부 ID)가 존재해야 함

        Args:
            db (Session): 데이터베이스 세션.
            team_create_request_dto (TeamCreateRequestDto): 팀 생성 요청 DTO.

        Returns:
            OrganizationDomain: 생성된 조직(팀) 도메인 객체.

        Raises:
            InvalidOrganizationLevelException: level이 3이 아닌 경우.
            MissingParentForTeamException: parent_seq가 없는 경우.
            InvalidHeadquarterIdException: 상위 본부가 유효하지 않은 경우.
        """
        if team_create_request_dto.level != 3:
            raise InvalidOrganizationLevelException()

        if team_create_request_dto.parent_seq is None:
            raise MissingParentForTeamException()

        existing_headquarters = self.organization_repository.get_organization_by_seq(db, team_create_request_dto.parent_seq)
        if not existing_headquarters or existing_headquarters.level != 2:
            raise InvalidHeadquarterIdException()

        team_domain = OrganizationDomain(**team_create_request_dto.model_dump())

        return self.organization_repository.create_organization(db=db, organization_domain=team_domain)

    @Transactional
    @History(entity="organization", action="UPDATE")
    def update_organization(self, db: Session, organization_seq: int, update_request: OrganizationNameAndVisibleUpdateRequestDto) -> OrganizationDomain:
        """
        특정 조직의 이름과 노출 여부를 업데이트 하는 메서드.
        - `name`, `is_visible` 변경 가능

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 수정할 조직 seq.
            update_request (OrganizationNameAndVisibleUpdateRequestDto): 수정할 데이터 DTO.

        Returns:
            OrganizationDomain: 수정된 조직 도메인 객체.

        Raises:
            OrganizationNotFoundException: 조직이 존재하지 않는 경우.
        """

        organization_domain = self.organization_repository.get_organization_by_seq(db, organization_seq)
        if organization_domain is None:
            raise OrganizationNotFoundException()

        update_data = update_request.model_dump(exclude_unset=True)

        if not update_data:
            return OrganizationUpdateDataNotFoundException()

        return self.organization_repository.update_organization(db, organization_seq, update_data)

    @Transactional
    @History(entity="organization", action="UPDATE")
    def move_organization(self, db: Session, organization_move_request: OrganizationMoveRequestDto) -> OrganizationDomain:
        """
        특정 조직을 새로운 조직으로 이동하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_move_request (OrganizationMoveRequestDto): 조직 이동 요청 DTO.

        Returns:
            OrganizationDomain: 이동된 조직 도메인 객체.

        Raises:
            OrganizationNotFoundException: 대상 또는 상위 조직이 존재하지 않는 경우.
        """
        # 조직 정보를 변경할 조직 seq
        organization_seq = organization_move_request.organization_seq
        organization_domain = self.organization_repository.get_organization_by_seq(db, organization_seq)
        if organization_domain is None:
            raise OrganizationNotFoundException()

        # 새 부모 조직 seq
        new_parent_seq = organization_move_request.new_parent_seq
        organization_domain = self.organization_repository.get_organization_by_seq(db, new_parent_seq)
        if organization_domain is None:
            raise OrganizationNotFoundException()

        return self.organization_repository.update_organization(db, organization_seq, update_data={"parent_seq": new_parent_seq})

    @Transactional
    @History(entity="organization", action="DELETE")
    def delete_organization(self, db: Session, organization_seq: int) -> bool:
        """
        특정 조직을 삭제하는 메서드.
        - 매핑 되어있는 직원이 있을 경우 삭제 불가.
        - 하위 조직이 있을 경우 삭제 불가.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 삭제할 조직 seq.

        Returns:
            bool: 삭제 성공 여부.

        Raises:
            EmployeesExistInOrganizationException: 직원이 소속된 경우.
            SubOrganizationsExistException: 하위 조직이 존재하는 경우.
            OrganizationNotFoundException: 조직이 존재하지 않는 경우.
        """

        # 삭제 하는 조직 ID 에 매핑 되어있는 직원이 있는지
        has_employees = self.employee_repository.count_employees_by_organization_seq(db, organization_seq)
        if has_employees > 0:
            raise EmployeesExistInOrganizationException()

        has_children = self.organization_repository.has_child_organizations(db, organization_seq)
        if has_children:
            raise SubOrganizationsExistException()

        organization_domain = self.organization_repository.get_organization_by_seq(db, organization_seq)
        if organization_domain is None:
            raise OrganizationNotFoundException()

        return self.organization_repository.delete_organization(db, organization_seq)

    @Transactional
    @History(entity="organization", action="UPDATE")
    def soft_delete_organization(self, db: Session, organization_seq: int) -> OrganizationDomain:
        """
        특정 조직을 논리적으로 삭제하는 메서드 (delete_at 필드 업데이트).
        - 매핑되어있는 직원이 있을 경우 소프트 삭제 불가.
        - 하위 조직이 있을 경우 소프트 삭제 불가.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 논리 삭제할 조직 seq.

        Returns:
            OrganizationDomain: 수정된 조직 도메인 객체.

        Raises:
            EmployeesExistInOrganizationException: 직원이 소속된 경우.
            SubOrganizationsExistException: 하위 조직이 존재하는 경우.
            OrganizationNotFoundException: 조직이 존재하지 않는 경우.
        """

        # 삭제 하는 조직 ID 에 매핑 되어있는 직원이 있는지
        has_employees = self.employee_repository.count_employees_by_organization_seq(db, organization_seq)
        if has_employees > 0:
            raise EmployeesExistInOrganizationException()

        # 하위 조직이 있는지
        has_children = self.organization_repository.has_child_organizations(db, organization_seq)
        if has_children:
            raise SubOrganizationsExistException()

        organization_domain = self.organization_repository.get_organization_by_seq(db, organization_seq)
        if organization_domain is None:
            raise OrganizationNotFoundException()

        return self.organization_repository.soft_delete_organization(db, organization_seq)

    def get_organization_tree(self, db: Session) -> List[OrganizationDomain]:
        """
        전체 조직도 계층 구조로 조회.

        Args:
            db (Session): 데이터베이스 세션.

        Returns:
            List[OrganizationDomain]: 계층 구조의 전체 조직 리스트.
        """
        return self.organization_repository.get_organization_tree(db)

