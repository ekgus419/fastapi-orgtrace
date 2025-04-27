from typing import Tuple, List
from sqlalchemy.orm import Session
from src.decorator.transaction import Transactional
from src.domain.rank_domain import RankDomain
from src.dto.request.rank.rank_create_request_dto import RankCreateRequestDto
from src.dto.request.rank.rank_update_request_dto import RankUpdateRequestDto
from src.exception.rank_exceptions import RankNotFoundException, RankAlreadyExistsException, \
    RankUpdateDataNotFoundException
from src.repository.rank.rank_repository import RankRepository
from src.service.base_service import BaseService


class RankService(BaseService):
    """
    직위(Rank) 관련 비즈니스 로직을 처리하는 서비스 클래스.
    데이터 접근 로직은 RankRepository를 통해 수행하며,
    도메인 로직을 적용하여 직위 관리 기능을 제공함.
    """

    def __init__(self, rank_repository: RankRepository):
        """
        RankService의 생성자.

        Args:
            rank_repository (RankRepository):
                직위 데이터 접근을 위한 RankRepository 인스턴스.
        """
        self.rank_repository = rank_repository

    def get_ranks(
        self,
        db: Session,
        page: int,
        size: int,
        sort_by: str | None,
        order: str
    ) -> Tuple[List[RankDomain], int]:
        """
        페이징 및 정렬을 적용하여 직위 목록을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str | None): 정렬할 컬럼명 (예: "seq", "name")
            order (str): 정렬 방식 ("asc" | "desc")

        Returns:
            Tuple[List[RankDomain], int]:
                직위 도메인 리스트와 전체 직위 수.
        """
        rank_domains = self.rank_repository.get_ranks(db, page, size, sort_by, order)
        total_count = self.rank_repository.count_ranks(db)
        return rank_domains, total_count

    def get_rank_by_seq(self, db: Session, rank_seq: int) -> RankDomain:
        """
        특정 직위 seq를 기반으로 직위 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 조회할 직위 seq.

        Returns:
            RankDomain: 조회된 직윈 도메인 객체.

        Raises:
            RankNotFoundException: 직위가 존재하지 않을 경우.
        """
        rank_domain = self.rank_repository.get_rank_by_seq(db, rank_seq)
        if rank_domain is None:
            raise RankNotFoundException()
        return rank_domain

    @Transactional
    def create_rank(self, db: Session, rank_create_request: RankCreateRequestDto) -> RankDomain:
        """
        새로운 직위을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션
            rank_create_request (RankCreateRequestDto): 직위 생성 요청 DTO

        Returns:
            RankDomain: 생성된 직위 도메인 객체.

        Raises:
            RankAlreadyExistsException: 동일한 title이 이미 존재하는 경우.
        """
        # 직위가 이미 존재하는지 확인
        existing_rank = self.rank_repository.get_rank_by_title(db, rank_create_request.title)
        if existing_rank:
            raise RankAlreadyExistsException()

        rank_domain = RankDomain(**rank_create_request.model_dump())

        return self.rank_repository.create_rank(db, rank_domain)

    @Transactional
    def update_rank(self, db: Session, rank_seq: int, update_request: RankUpdateRequestDto) -> RankDomain:
        """
        특정 직위 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 수정할 직위 seq.
            update_request (RankUpdateRequestDto): 수정할 데이터 DTO

        Returns:
            RankDomain: 수정된 직위 도메인 객체.

        Raises:
            RankNotFoundException: 해당 직위가 존재하지 않는 경우.
            RankUpdateDataNotFoundException: 수정할 데이터가 없을 경우.
        """
        rank_domain = self.rank_repository.get_rank_by_seq(db, rank_seq)
        if rank_domain is None:
            raise RankNotFoundException()

        # DTO를 dict로 변환
        update_data = update_request.model_dump(exclude_unset=True)

        if not update_data:
            return RankUpdateDataNotFoundException()

        return self.rank_repository.update_rank(db, rank_seq, update_data)

    @Transactional
    def delete_rank(self, db: Session, rank_seq: int) -> bool:
        """
        특정 직위를 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 삭제할 직위 seq.

        Returns:
            bool: 삭제 성공 여부.

        Raises:
            RankNotFoundException: 해당 직위가 존재하지 않을 경우.
        """
        rank_domain = self.rank_repository.get_rank_by_seq(db, rank_seq)
        if rank_domain is None:
            raise RankNotFoundException()

        return self.rank_repository.delete_rank(db, rank_seq)

    @Transactional
    def soft_delete_rank(self, db: Session, rank_seq: int) -> RankDomain:
        """
        특정 직위를 논리적으로 삭제하는 메서드 (delete_at 필드 업데이트).

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 논리 삭제할 직위 seq.

        Returns:
            RankDomain: 수정된 직위 도메인 객체.

        Raises:
            RankNotFoundException: 해당 직위가 존재하지 않을 경우.
        """
        rank_domain = self.rank_repository.get_rank_by_seq(db, rank_seq)
        if rank_domain is None:
            raise RankNotFoundException()

        return self.rank_repository.soft_delete_rank(db, rank_seq)
