from typing import Optional, List
from sqlalchemy.orm import Session
from src.entity.rank_entity import RankEntity
from src.repository.base_repository import BaseRepository
from src.mapper.rank_mapper import entity_to_domain, domain_to_entity
from src.domain.rank_domain import RankDomain

class RankRepository(BaseRepository[RankEntity]):
    """
    직위(Rank) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통적인 CRUD 기능은 BaseRepository에서 상속받고,
    직위 관련 추가 기능을 여기에 정의함.
    """

    def __init__(self):
        """
        RankRepository 생성자.
        """
        super().__init__(RankEntity)

    def get_ranks(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = None,
        order: str = "asc"
    ) -> List[RankDomain]:
        """
        페이징 및 정렬을 적용하여 모든 직위를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str): 정렬할 컬럼명 (예: "seq", "title").
            order (str): 정렬 방식 ("asc" 또는 "desc").

        Returns:
            List[RankDomain]: 조회된 직위 목록 (RankDomain 객체 리스트).
        """
        rank_entities = self.find_all(db=db, page=page, size=size, sort_by=sort_by, order=order)
        return [entity_to_domain(rank) for rank in rank_entities]

    def count_ranks(self, db: Session) -> int:
        """
        전체 직위 수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.

        Returns:
            int: 직위 총 개수.
        """
        return self.count_all(db=db)

    def get_rank_by_seq(self, db: Session, rank_seq: int) -> Optional[RankDomain]:
        """
        직위 seq를 기반으로 단일 직위를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 조회할 직위의 순번(seq).

        Returns:
            Optional[RankDomain]: 조회된 RankDomain 객체 (없을 경우 None).
        """
        entity = self.find_by_id(db=db, entity_id=rank_seq)
        return entity_to_domain(entity) if entity else None

    def get_rank_by_title(self, db: Session, title: str) -> Optional[RankDomain]:
        """
        직위명을 기반으로 직위를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            title (str): 조회할 직위명.

        Returns:
            Optional[RankDomain]: 조회된 직위 객체 (없을 경우 None).
        """
        entity = db.query(self.entity).filter(self.entity.title == title).first()

        if entity:
            entity = db.merge(entity)
            db.refresh(entity)

        return entity_to_domain(entity) if entity else None

    def create_rank(self, db: Session, rank_domain: RankDomain) -> RankDomain:
        """
        새로운 직위를 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_domain (RankDomain): 저장할 RankDomain 객체.

        Returns:
            RankDomain: 저장된 RankDomain 객체.
        """
        entity = domain_to_entity(rank_domain)
        saved_entity = self.save(db=db, entity=entity)
        return entity_to_domain(saved_entity)

    def update_rank(self, db: Session, rank_seq: int, update_data: dict) -> RankDomain:
        """
        특정 직위 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 수정할 직위 seq.
            update_data (dict): 수정할 직위 정보.

        Returns:
            RankDomain: 수정된 RankDomain 객체.
        """
        updated = self.update(db=db, entity_id=rank_seq, **update_data)
        return updated

    def delete_rank(self, db: Session, rank_seq: int) -> bool:
        """
        특정 seq의 직위를 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 삭제할 직위 seq.

        Returns:
            bool: 삭제 성공 여부 (True/False).
        """
        return self.delete_by_id(db=db, entity_id=rank_seq)

    def soft_delete_rank(self, db: Session, rank_seq: int) -> RankDomain:
        """
        특정 seq의 직위를 논리 삭제하는 메서드.
        실제 데이터는 삭제하지 않고, delete_at 필드를 업데이트합니다.

        Args:
            db (Session): 데이터베이스 세션.
            rank_seq (int): 논리 삭제할 직위 seq.

        Returns:
            RankDomain: 수정된 RankDomain 객체.
        """
        return self.soft_delete_by_id(db=db, entity_id=rank_seq)

