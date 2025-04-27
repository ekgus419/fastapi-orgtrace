from typing import Tuple, List
from sqlalchemy.orm import Session
from src.decorator.transaction import Transactional  # 트랜잭션 데코레이터 추가
from src.domain.position_domain import PositionDomain
from src.dto.request.position.position_create_request_dto import PositionCreateRequestDto
from src.dto.request.position.position_update_request_dto import PositionUpdateRequestDto
from src.exception.position_exceptions import PositionNotFoundException, PositionAlreadyExistsException, \
    PositionUpdateDataNotFoundException
from src.repository.position.position_repository import PositionRepository
from src.service.base_service import BaseService


class PositionService(BaseService):
    """
    직책(Position) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근 로직은 PositionRepository를 통해 수행하며,
    도메인 로직을 적용하여 직책 관리 기능을 제공함.
    """

    def __init__(self, position_repository: PositionRepository):
        """
        PositionService의 생성자.

        Args:
            position_repository (PositionRepository):
                직책 데이터 접근을 위한 PositionRepository 인스턴스
        """
        self.position_repository = position_repository

    def get_positions(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str
    ) -> Tuple[List[PositionDomain], int]:
        """
        페이징 및 정렬을 적용하여 직책 목록을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "name")
            order (str): 정렬 방식 ("asc" | "desc")

        Returns:
            Tuple[List[PositionDomain], int]:
                조회된 직책 리스트와 전체 직책 수.
        """
        position_domains = self.position_repository.get_positions(db, page, size, sort_by, order)
        total_count = self.position_repository.count_positions(db)
        return position_domains, total_count

    def get_position_by_seq(self, db: Session, position_seq: int) -> PositionDomain:
        """
        특정 직책 seq를 기반으로 직책 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 조회할 직책 seq.

        Returns:
            PositionDomain: 조회된 직책 도메인 객체.

        Raises:
            PositionNotFoundException: 직책이 존재하지 않을 경우.
        """
        position_domain = self.position_repository.get_position_by_seq(db, position_seq)
        if position_domain is None:
            raise PositionNotFoundException()
        return position_domain

    @Transactional
    def create_position(self, db: Session, position_create_request: PositionCreateRequestDto) -> PositionDomain:
        """
        새로운 직책을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_create_request (PositionCreateRequestDto): 직책 생성 요청 DTO.

        Returns:
            PositionDomain: 생성된 직책 도메인 객체.

        Raises:
            PositionAlreadyExistsException: 동일한 title이 이미 존재하는 경우.
        """
        # 직책이 이미 존재하는지 확인
        existing_position = self.position_repository.get_position_by_title(db, position_create_request.title)
        if existing_position:
            raise PositionAlreadyExistsException()

        position_domain = PositionDomain(**position_create_request.model_dump())

        return self.position_repository.create_position(db, position_domain)

    @Transactional
    def update_position(self, db: Session, position_seq: int, update_request: PositionUpdateRequestDto) -> PositionDomain:
        """
        특정 직책 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 수정할 직책 seq.
            update_request (PositionUpdateRequestDto): 수정할 데이터 DTO.

        Returns:
            PositionDomain: 수정된 직책 도메인 객체.

        Raises:
            PositionNotFoundException: 해당 직책이 존재하지 않을 경우.
        """
        position_domain = self.position_repository.get_position_by_seq(db, position_seq)
        if position_domain is None:
            raise PositionNotFoundException()

        # DTO를 dict로 변환
        update_data = update_request.model_dump(exclude_unset=True)

        if not update_data:
            return PositionUpdateDataNotFoundException()

        return self.position_repository.update_position(db, position_seq, update_data)

    @Transactional
    def delete_position(self, db: Session, position_seq: int) -> bool:
        """
        특정 직책을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 삭제할 직책 seq.

        Returns:
            bool: 삭제 성공 여부.

        Raises:
            PositionNotFoundException: 해당 직책이 존재하지 않을 경우.
        """
        position_domain = self.position_repository.get_position_by_seq(db, position_seq)
        if position_domain is None:
            raise PositionNotFoundException()

        return self.position_repository.delete_position(db, position_seq)

    @Transactional
    def soft_delete_position(self, db: Session, position_seq: int) -> PositionDomain:
        """
        특정 직책을 논리적으로 삭제하는 메서드 (delete_at 필드 업데이트).

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 논리 삭제할 직책 seq.

        Returns:
            PositionDomain: 수정된 직책 도메인 객체.

        Raises:
            PositionNotFoundException: 해당 직책이 존재하지 않을 경우.
        """
        position_domain = self.position_repository.get_position_by_seq(db, position_seq)
        if position_domain is None:
            raise PositionNotFoundException()

        return self.position_repository.soft_delete_position(db, position_seq)
