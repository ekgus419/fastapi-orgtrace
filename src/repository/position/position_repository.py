from typing import Optional, List
from sqlalchemy.orm import Session
from src.entity.position_entity import PositionEntity
from src.repository.base_repository import BaseRepository
from src.mapper.position_mapper import entity_to_domain, domain_to_entity
from src.domain.position_domain import PositionDomain

class PositionRepository(BaseRepository[PositionEntity]):
    """
    직책(Position) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통적인 CRUD 기능은 BaseRepository에서 상속받고,
    직책 관련 추가 기능을 여기에 정의함.
    """

    def __init__(self):
        """
        PositionRepository 생성자.
        """
        super().__init__(PositionEntity)

    def get_positions(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = None,
        order: str = "asc"
    ) -> List[PositionDomain]:
        """
        페이징 및 정렬을 적용하여 모든 직책을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str): 정렬할 컬럼명 (예: "seq", "title").
            order (str): 정렬 방식 ("asc" | "desc").

        Returns:
            List[PositionDomain]: 조회된 직책 목록 (PositionDomain 객체 리스트).
        """
        position_entities = self.find_all(db=db, page=page, size=size, sort_by=sort_by, order=order)
        return [entity_to_domain(position) for position in position_entities]

    def count_positions(self, db: Session) -> int:
        """
        전체 직책 수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.

        Returns:
            int: 직책 총 개수.
        """
        return self.count_all(db=db)

    def get_position_by_seq(self, db: Session, position_seq: int) -> Optional[PositionDomain]:
        """
        직책 seq를 기반으로 단일 직책을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 조회할 직책 seq.

        Returns:
            Optional[PositionDomain]: 조회된 직책 도메인 객체 (없으면 None).
        """
        entity = self.find_by_id(db=db, entity_id=position_seq)
        return entity_to_domain(entity) if entity else None

    def get_position_by_title(self, db: Session, title: str) -> Optional[PositionDomain]:
        """
        직책명을 기반으로 직책 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            title (str): 조회할 직책명.

        Returns:
            Optional[PositionDomain]: 조회된 직책 도메인 객체 (없으면 None).
        """
        entity = db.query(self.entity).filter(self.entity.title == title).first()

        if entity:
            entity = db.merge(entity)
            db.refresh(entity)

        return entity_to_domain(entity) if entity else None

    def create_position(self, db: Session, position_domain: PositionDomain) -> PositionDomain:
        """
        새로운 직책을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_domain (PositionDomain): 저장할 PositionDomain 객체.

        Returns:
            PositionDomain: 저장된 PositionDomain 객체.
        """
        entity = domain_to_entity(position_domain)
        saved_entity = self.save(db=db, entity=entity)
        return entity_to_domain(saved_entity)

    def update_position(self, db: Session, position_seq: int, update_data: dict) -> PositionDomain:
        """
        특정 직책 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 직책 정보를 변경할 직책 seq.
            update_data (dict): 수정할 직책 정보.

        Returns:
            PositionDomain: 수정된 PositionDomain 객체.
        """
        updated = self.update(db=db, entity_id=position_seq, **update_data)
        return updated

    def delete_position(self, db: Session, position_seq: int) -> bool:
        """
        특정 seq의 직책을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 삭제할 직책 seq.

        Returns:
            bool: 삭제 성공 여부 (True/False).
        """
        return self.delete_by_id(db=db, entity_id=position_seq)

    def soft_delete_position(self, db: Session, position_seq: int) -> PositionDomain:
        """
        특정 seq의 직책을 논리 삭제하는 메서드.
        실제 데이터는 삭제하지 않고, delete_at 필드를 업데이트함.

        Args:
            db (Session): 데이터베이스 세션.
            position_seq (int): 삭제할 직책 seq.

        Returns:
            PositionDomain: 수정된 PositionDomain 객체.
        """
        return self.soft_delete_by_id(db=db, entity_id=position_seq)