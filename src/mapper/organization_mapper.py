from src.domain.organization_domain import OrganizationDomain
from src.entity.organization_entity import OrganizationEntity


def entity_to_domain(organization_entity: OrganizationEntity) -> OrganizationDomain:
    """
    (ORM 엔티티 → 도메인 객체 변환)
    ORM Entity를 도메인 객체로 변환합니다.
    Entity는 ORM(SQLAlchemy)에서 직접 사용하는 데이터베이스 모델이며,
    Domain은 비즈니스 로직을 수행하는 도메인 객체입니다.
    도메인 계층에서 데이터베이스 종속성을 줄이기 위해 Domain으로 변환하여 사용합니다.
    """
    return OrganizationDomain(
        seq=organization_entity.seq,
        name=organization_entity.name,
        level=organization_entity.level,
        parent_seq=organization_entity.parent_seq,
        is_visible=organization_entity.is_visible,
        created_at=organization_entity.created_at,
        updated_at=organization_entity.updated_at,
        deleted_at=organization_entity.deleted_at,
    )


def domain_to_entity(organization_domain: OrganizationDomain) -> OrganizationEntity:
    """
    (도메인 객체 → ORM 엔티티 변환)
    Doamin 객체를 ORM Entity로 변환합니다.
    """
    return OrganizationEntity(
        name=organization_domain.name,
        level=organization_domain.level,
        parent_seq=organization_domain.parent_seq,
        is_visible=organization_domain.is_visible,
    )