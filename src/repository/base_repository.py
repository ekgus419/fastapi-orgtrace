from typing import Type, TypeVar, Generic, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, asc, inspect, delete, func, and_
from sqlalchemy.sql.expression import ColumnElement
from src.entity.base_entity import Base  # SQLAlchemy Base 클래스

# T가 항상 SQLAlchemy의 Base를 상속하는 모델이 되도록 제한
T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    공통적인 데이터 접근 로직을 제공하는 추상 클래스.
    모든 엔티티 리포지토리는 이 클래스를 상속받아 공통 기능을 재사용함.
    """

    def __init__(self, entity: Type[T]):
        """
        :param entity: ORM 모델 클래스 (Base를 상속해야 함)
        """
        self.entity = entity

        # 기본 키가 존재하는지 체크
        primary_keys = inspect(self.entity).primary_key
        if not primary_keys:
            raise ValueError(f"{self.entity.__name__} 모델에 기본 키가 없습니다.")

        # 기본 키 컬럼을 SQLAlchemy InstrumentedAttribute로 변환
        # 기본 키의 이름 가져오기
        primary_key_name = primary_keys[0].name
        # SQLAlchemy 컬럼 객체로 변환
        self.primary_key: ColumnElement = getattr(self.entity, primary_key_name)

    def find_all(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: Optional[str] = None,
        order: str = "asc",
        filters: Optional[list] = None  # 필터 조건을 리스트로 받음
    ) -> List[T]:
        """
        페이징 및 정렬을 지원하는 목록 조회 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1-based 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (Optional[str]): 정렬할 컬럼명 (예: "seq", "username").
            order (str): 정렬 방식 ("asc" 또는 "desc").
            filters (Optional[list]): (선택) 필터 조건 리스트 (예: [self.entity.level == 1, self.entity.status == 'active']).

        Returns:
            List[T]: 조회된 목록.
        """
        query = db.query(self.entity)

        # filters가 제공되면 이를 쿼리에 적용
        if filters:
            query = query.filter(and_(*filters))

        # 정렬 컬럼 유효성 체크
        if sort_by:
            entity_columns = {column.name for column in inspect(self.entity).c}
            if sort_by not in entity_columns:
                raise ValueError(f"정렬할 컬럼 '{sort_by}'가 존재하지 않습니다. 사용 가능한 컬럼: {entity_columns}")

            sort_attr = getattr(self.entity, sort_by)
            query = query.order_by(desc(sort_attr) if order.lower() == "desc" else asc(sort_attr))

        # 페이징 적용
        return query.offset((page - 1) * size).limit(size).all()

    def find_by_id(self, db: Session, entity_id: int) -> Optional[T]:
        """
        ID를 기반으로 엔티티를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            entity_id (int): 조회할 Entity ID.

        Returns:
            Optional[T]: 조회된 엔티티 (없으면 None).
        """
        return db.query(self.entity).filter(self.primary_key == entity_id).first()

    def count_all(self, db: Session, filters=None) -> int:
        """
        전체 엔티티 개수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            filters (Optional): 검색 조건.

        Returns:
            int: 전체 엔티티 개수.
        """
        query = db.query(self.entity)

        if filters:
            query = query.filter(and_(*filters))

        return query.count()

    def save(self, db: Session, entity: T) -> T:
        """
        엔티티를 데이터베이스에 저장하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            entity (T): 저장할 엔티티.

        Returns:
            T: 저장된 엔티티.
        """
        try:
            db.add(entity)
            db.flush()  # 변경 사항을 DB에 즉시 반영
            db.refresh(entity)
            return entity
        except Exception as e:
            db.rollback()
            raise e

    def update(self, db: Session, entity_id: int, **kwargs) -> Optional[T]:
        """
        특정 ID의 엔티티를 업데이트하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            entity_id (int): 수정할 엔티티 ID.
            kwargs (dict): 수정할 필드 및 값.

        Returns:
            Optional[T]: 업데이트된 엔티티 (없으면 None).
        """
        entity = db.query(self.entity).filter(self.primary_key == entity_id).first()
        if not entity:
            return None

        entity_columns = {column.name for column in inspect(self.entity).c}
        valid_data = {key: value for key, value in kwargs.items() if key in entity_columns}

        for key, value in valid_data.items():
            setattr(entity, key, value)

        try:
            db.flush()
            db.refresh(entity)
            return entity
        except Exception as e:
            db.rollback()
            raise e

    def delete_by_id(self, db: Session, entity_id: int) -> bool:
        """
        특정 ID의 엔티티를 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            entity_id (int): 삭제할 엔티티 ID.

        Returns:
            bool: 삭제 성공 여부.
        """
        stmt = delete(self.entity).where(self.primary_key == entity_id)
        try:
            result = db.execute(stmt)
            db.flush()
            return bool(result.rowcount)
        except Exception as e:
            db.rollback()
            raise e

    def soft_delete_by_id(self, db: Session, entity_id: int) -> Optional[T]:
        """
        특정 ID의 엔티티를 소프트 삭제하는 메서드.
        실제 데이터는 삭제하지 않고, delete_at 컬럼에 삭제 시점을 기록합니다.

        Args:
            db (Session): 데이터베이스 세션.
            entity_id (int): 소프트 삭제할 엔티티 ID.

        Returns:
            Optional[T]: 소프트 삭제된 엔티티 (없으면 None).
        """
        entity = db.query(self.entity).filter(self.primary_key == entity_id).first()

        if not entity:
            return None
        try:
            entity.deleted_at = func.now()
            db.flush()
            db.refresh(entity)
            return entity
        except Exception as e:
            db.rollback()
            raise e

    def exists_by_id(self, db: Session, entity_id: int) -> bool:
        """
        특정 ID의 엔티티 존재 여부를 확인하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            entity_id (int): 확인할 엔티티 ID.

        Returns:
            bool: 존재 여부 (True/False).
        """
        return db.query(self.entity).filter(self.primary_key == entity_id).first() is not None

    def find_by_native_query(self, db: Session, sql: str,
                             params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        네이티브 SQL 쿼리를 실행하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            sql (str): 실행할 네이티브 SQL 쿼리.
            params (Optional[Dict[str, Any]]): SQL 쿼리의 파라미터.

        Returns:
            List[Dict[str, Any]]: 쿼리 결과를 딕셔너리 형태로 반환.
        """
        result = db.execute(text(sql), params or {}).mappings().all()
        return [dict(row) for row in result]
