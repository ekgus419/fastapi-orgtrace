from typing import Tuple, List
from sqlalchemy.orm import Session
from src.dto.request.user.user_create_request_dto import UserCreateRequestDto
from src.exception.user_exceptions import UserNotFoundException, UserAlreadyExistsException
from src.repository.user.user_repository import UserRepository
from src.service.base_service import BaseService
from src.utils.security import hash_password
from src.domain.user_domain import UserDomain
from src.decorator.transaction import Transactional  # 트랜잭션 데코레이터 추가


class UserService(BaseService):
    """
    회원(User) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근 로직은 UserRepository를 통해 수행하며,
    도메인 로직을 적용하여 회원 관리 기능을 제공함.
    """

    def __init__(self, user_repository: UserRepository):
        """
        UserService의 생성자.

        Args:
            user_repository (UserRepository):
                회원 데이터 접근을 위한 UserRepository 인스턴스.
        """
        self.user_repository = user_repository

    def get_users(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str
    ) -> Tuple[List[UserDomain], int]:
        """
        페이징 및 정렬을 적용하여 회원 목록을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "username")
            order (str): 정렬 방식 ("asc" | "desc")

        Returns:
            Tuple[List[UserDomain], int]:
                회원 도메인 리스트와 전체 회원 수.
        """
        user_domains = self.user_repository.get_users(db, page, size, sort_by, order)
        total_count = self.user_repository.count_users(db)
        return user_domains, total_count

    def get_user_by_seq(self, db: Session, user_seq: int) -> UserDomain:
        """
        특정 회원 seq를 기반으로 회원 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 조회할 회원 seq.

        Returns:
            UserDomain: 조회된 회원 도메인 객체.

        Raises:
            UserNotFoundException: 회원이 존재하지 않을 경우.
        """
        user_domain = self.user_repository.get_user_by_seq(db, user_seq)
        if user_domain is None:
            raise UserNotFoundException()
        return user_domain

    @Transactional
    def create_user(self, db: Session, user_create_request: UserCreateRequestDto) -> UserDomain:
        """
        새로운 회원을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_create_request (UserCreateRequestDto): 회원 생성 요청 DTO.

        Returns:
            UserDomain: 생성된 회원 도메인 객체.

        Raises:
            UserAlreadyExistsException: 동일한 username을 가진 회원이 이미 존재하는 경우.
        """
        # 유저가 이미 존재하는지 확인
        existing_user = self.user_repository.get_user_by_username(db, user_create_request.username)
        if existing_user:
            raise UserAlreadyExistsException()

        hashed_password = hash_password(user_create_request.password)
        user_create_request.type = user_create_request.type or 100
        user_create_request.status = user_create_request.status or 100

        user_domain = UserDomain(**user_create_request.model_dump())

        # Repository에서 저장 후 Domain 반환
        return self.user_repository.create_user(db, user_domain, hashed_password)

    @Transactional
    def update_password(self, db: Session, user_seq: int, new_password: str) -> UserDomain:
        """
        회원의 비밀번호를 변경하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 비밀번호를 변경할 회원 seq.
            new_password (str): 변경할 새 비밀번호 (평문).

        Returns:
            bool: 비밀번호 변경 성공 여부.

        Raises:
            UserNotFoundException: 해당 회원이 존재하지 않을 경우.
        """
        user_domain = self.user_repository.get_user_by_seq(db, user_seq)
        if user_domain is None:
            raise UserNotFoundException

        hashed_password = hash_password(new_password)
        return self.user_repository.update_password(db, user_seq, hashed_password)

    @Transactional
    def delete_user(self, db: Session, user_seq: int) -> bool:
        """
        특정 회원을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 삭제할 회원 seq.

        Returns:
            bool: 삭제 성공 여부.

        Raises:
            UserNotFoundException: 해당 회원이 존재하지 않을 경우.
        """
        user_domain = self.user_repository.get_user_by_seq(db, user_seq)
        if user_domain is None:
            raise UserNotFoundException

        return self.user_repository.delete_user(db, user_seq)

    @Transactional
    def soft_delete_user(self, db: Session, user_seq: int) -> UserDomain:
        """
        특정 회원을 논리적으로 삭제하는 메서드 (delete_at 필드 업데이트).

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 논리 삭제할 회원 seq.

        Returns:
            bool: 수정된 회원 도메인 객체.

        Raises:
            UserNotFoundException: 해당 회원이 존재하지 않을 경우.
        """
        user_domain = self.user_repository.get_user_by_seq(db, user_seq)
        if user_domain is None:
            raise UserNotFoundException()

        return self.user_repository.soft_delete_user(db, user_seq)