from typing import Optional, List
from sqlalchemy.orm import Session
from src.entity.user_entity import UserEntity
from src.repository.base_repository import BaseRepository
from src.mapper.user_mapper import entity_to_domain, domain_to_entity
from src.domain.user_domain import UserDomain

class UserRepository(BaseRepository[UserEntity]):
    """
    회원(User) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통적인 CRUD 기능은 BaseRepository에서 상속받고,
    회원 관련 추가 기능을 여기에 정의함.
    """

    def __init__(self):
        """
        UserRepository의 생성자.
        """
        super().__init__(UserEntity)

    def get_users(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = None,
        order: str = "asc",
    ) -> List[UserDomain]:
        """
        페이징 및 정렬을 적용하여 모든 회원을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지당 가져올 데이터 개수.
            sort_by (str): 정렬할 컬럼명 (예: "seq", "username").
            order (str): 정렬 방식 ("asc" 또는 "desc").

        Returns:
            List[UserDomain]: 조회된 회원 목록 (UserDomain 객체 리스트).
        """
        user_entities = self.find_all(db=db, page=page, size=size, sort_by=sort_by, order=order)
        return [entity_to_domain(user) for user in user_entities]

    def count_users(self, db: Session) -> int:
        """
        전체 회원 수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.

        Returns:
            int: 회원 총 개수.
        """
        return self.count_all(db=db)

    def get_user_by_seq(self, db: Session, user_seq: int) -> Optional[UserDomain]:
        """
        회원 seq를 기반으로 단일 회원을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 조회할 회원 seq.

        Returns:
            Optional[UserDomain]: 조회된 UserDomain 객체 (없을 경우 None).
        """
        entity = self.find_by_id(db=db, entity_id=user_seq)
        return entity_to_domain(entity) if entity else None

    def get_user_by_username(self, db: Session, username: str) -> Optional[UserDomain]:
        """
        회원 아이디를 기반으로 회원 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            username (str): 조회할 회원 아이디.

        Returns:
            Optional[UserDomain]: 조회된 UserDomain 객체 (없을 경우 None).
        """
        entity = db.query(self.entity).filter(self.entity.username == username).first()

        if entity:
            entity = db.merge(entity)
            db.refresh(entity)

        return entity_to_domain(entity) if entity else None

    def create_user(self, db: Session, user_domain: UserDomain, hashed_password: str) -> UserDomain:
        """
        새로운 회원을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_domain (UserDomain): 저장할 UserDomain 객체.
            hashed_password (str): 해싱된 비밀번호.

        Returns:
            UserDomain: 저장된 UserDomain 객체.
        """
        entity = domain_to_entity(user_domain, hashed_password)
        saved_entity = self.save(db=db, entity=entity)
        return entity_to_domain(saved_entity)

    def update_password(self, db: Session, user_seq: int, hashed_password: str) -> UserDomain:
        """
        특정 회원의 비밀번호를 업데이트하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 비밀번호를 변경할 회원의 순번(seq).
            hashed_password (str): 해싱된 새 비밀번호.

        Returns:
            UserDomain: 수정된 UserDomain 객체.
        """
        updated = self.update(db=db, entity_id=user_seq, password=hashed_password)
        return updated

    def delete_user(self, db: Session, user_seq: int) -> bool:
        """
        특정 seq의 회원을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 삭제할 회원 seq.

        Returns:
            bool: 삭제 성공 여부.
        """
        return self.delete_by_id(db=db, entity_id=user_seq)

    def soft_delete_user(self, db: Session, user_seq: int) -> UserDomain:
        """
        특정 seq의 회원을 논리 삭제하는 메서드.
        실제 데이터는 삭제하지 않고, delete_at 필드를 업데이트합니다.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 논리 삭제할 회원 seq.

        Returns:
            UserDomain: 수정된 UserDomain 객체.
        """
        return self.soft_delete_by_id(db=db, entity_id=user_seq)

    def update_refresh_token(self, db: Session, user_seq: int, refresh_token: Optional[str]) -> bool:
        """
        회원의 Refresh Token을 업데이트하는 메서드.
        로그아웃 시에는 None으로 설정하여 토큰을 무효화함.

        Args:
            db (Session): 데이터베이스 세션.
            user_seq (int): 업데이트할 회원의 순번(seq).
            refresh_token (Optional[str]): 저장할 Refresh Token (None이면 로그아웃 처리).

        Returns:
            bool: 수정 성공 여부.
        """
        updated = self.update(db=db, entity_id=user_seq, current_refresh_token=refresh_token)
        return updated
