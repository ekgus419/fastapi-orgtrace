from typing import Optional, List
from sqlalchemy.orm import Session
from src.entity.organization_entity import OrganizationEntity
from src.repository.base_repository import BaseRepository
from src.mapper.organization_mapper import entity_to_domain, domain_to_entity
from src.domain.organization_domain import OrganizationDomain

class OrganizationRepository(BaseRepository[OrganizationEntity]):
    """
    조직(Organization) 엔티티의 데이터 접근을 담당하는 리포지토리 클래스.
    공통적인 CRUD 기능은 BaseRepository에서 상속받고,
    조직 관련 추가 기능을 여기에 정의함.
    """

    def __init__(self):
        """
        OrganizationRepository 생성자.
        """
        super().__init__(OrganizationEntity)

    def get_organizations(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = None,
        order: str = "asc",
        filters: Optional[list] = None
    ) -> List[OrganizationDomain]:
        """
        페이징 및 정렬을 적용하여 모든 조직을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            page (int): 1부터 시작하는 페이지 번호.
            size (int): 한 페이지에 가져올 데이터 개수.
            sort_by (str): 정렬할 컬럼명 (예: "seq", "name").
            order (str): 정렬 방식 ("asc" | "desc").
            filters (Optional[list]): 필터 조건, 예: level, parent_seq.

        Returns:
            List[OrganizationDomain]: 조회된 조직 목록 (OrganizationDomain 객체 리스트).
        """
        organization_entities = self.find_all(db=db, page=page, size=size, sort_by=sort_by, order=order, filters=filters)
        return [entity_to_domain(organization) for organization in organization_entities]

    def count_organizations(self, db: Session, filters=None) -> int:
        """
        전체 조직 수를 반환하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            filters (Optional[list]): 필터 조건.

        Returns:
            int: 조직 총 개수.
        """
        return self.count_all(db=db, filters=filters)

    def get_organization_by_seq(self, db: Session, organization_seq: int) -> Optional[OrganizationDomain]:
        """
        조직 seq를 기반으로 단일 조직을 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 조회할 조직 seq.

        Returns:
            Optional[OrganizationDomain]: 조회된 조직 도메인 객체 (없으면 None).
        """
        entity = self.find_by_id(db=db, entity_id=organization_seq)
        return entity_to_domain(entity) if entity else None

    def get_organization_by_name(self, db: Session, name: str) -> Optional[OrganizationDomain]:
        """
        조직명을 기반으로 조직 정보를 조회하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            name (str): 조회할 조직명.

        Returns:
            Optional[OrganizationDomain]: 조회된 조직 도메인 객체 (없으면 None).
        """
        entity = db.query(self.entity).filter(self.entity.name == name).first()

        if entity:
            entity = db.merge(entity)
            db.refresh(entity)

        return entity_to_domain(entity) if entity else None

    def create_organization(self, db: Session, organization_domain: OrganizationDomain) -> OrganizationDomain:
        """
        새로운 조직을 생성하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_domain (OrganizationDomain): 저장할 OrganizationDomain 객체.

        Returns:
            OrganizationDomain: 저장된 OrganizationDomain 객체.
        """
        entity = domain_to_entity(organization_domain)
        saved_entity = self.save(db=db, entity=entity)
        return entity_to_domain(saved_entity)

    def update_organization(self, db: Session, organization_seq: int, update_data: dict) -> OrganizationDomain:
        """
        특정 조직 정보를 수정하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 수정할 조직 seq.
            update_data (dict): 수정할 조직 정보.

        Returns:
            OrganizationDomain: 수정된 OrganizationDomain 객체.
        """
        updated = self.update(db=db, entity_id=organization_seq, **update_data)
        return updated

    def delete_organization(self, db: Session, organization_seq: int) -> bool:
        """
        특정 seq의 조직을 삭제하는 메서드.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 삭제할 조직 seq.

        Returns:
            bool: 삭제 성공 여부 (True/False).
        """
        return self.delete_by_id(db=db, entity_id=organization_seq)

    def soft_delete_organization(self, db: Session, organization_seq: int) -> OrganizationDomain:
        """
        특정 seq의 조직을 논리 삭제하는 메서드.
        실제 데이터는 삭제하지 않고, delete_at 필드를 업데이트함.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 논리 삭제할 조직 seq.

        Returns:
            OrganizationDomain: 수정된 OrganizationDomain 객체.
        """
        return self.soft_delete_by_id(db=db, entity_id=organization_seq)

    def has_child_organizations(self, db: Session, organization_seq: int) -> bool:
        """
        특정 조직이 하위 조직을 가지고 있는지 확인.

        Args:
            db (Session): 데이터베이스 세션.
            organization_seq (int): 조직 seq.

        Returns:
            bool: 하위 조직 존재 여부 (True/False).
        """
        # parent_seq 값으로 하위 조직을 가지고 있는지 확인
        return db.query(self.entity).filter(self.entity.parent_seq == organization_seq).count() > 0

    def get_organization_tree(self, db: Session) -> List[OrganizationDomain]:
        """
        조직 데이터를 계층 구조(Tree 구조)로 변환하여 반환한다.

        Args:
            db (Session): 데이터베이스 세션.

        Returns:
            List[OrganizationDomain]: 계층 구조로 변환된 전체 조직 목록.
        """
        total_organization_count = self.count_organizations(db)

        """
        필터링이나 정렬 옵션 없이, 전체 조직 목록을 페이지 1로 요청하여 모든 조직을 가져온다.
        page=1, size=전체 조직 수로 요청하여 한 번에 모든 데이터를 가져오도록 설정한다.
        """
        all_organizations = self.get_organizations(page=1, size=total_organization_count, sort_by=None, order="asc", filters=[], db=db)

        def build_tree(parent_seq: Optional[int]) -> List[OrganizationDomain]:
            """
            주어진 parent_seq에 해당하는 조직을 찾고, 그 조직들의 하위 조직들을 재귀적으로 찾아 트리 구조를 만든다.

            Args:
                parent_seq (Optional[int]): 부모 조직의 순번(주로 상위 조직의 순번). None일 경우 최상위 조직을 의미한다.

            Returns:
                List[OrganizationDomain]: 주어진 parent_seq에 해당하는 조직 목록을 계층 구조로 반환.
            """
            import dataclasses
            """
            각 조직에 대해 자식 조직(children)을 설정하는데, 자식 조직도 build_tree를 통해 재귀적으로 찾아 추가한다.
            dataclasses.replace를 사용하여 원본 객체를 수정하지 않고 새로운 객체를 반환한다.
            children 필드를 갱신한 새로운 객체가 반환되므로, 중복되는 자식 조직을 추가하지 않고 계층 구조를 정확히 구성할 수 있다.
            """
            return [
                dataclasses.replace(org, children=build_tree(org.seq))        # 원본 객체를 수정하지 않고 새로운 객체를 반환
                for org in all_organizations if org.parent_seq == parent_seq  # 현재 부모 조직에 해당하는 자식 조직만 필터링
            ]

        # 최상위 조직부터 트리 구조를 생성하여 반환한다.
        return build_tree(None)
