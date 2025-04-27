from src.entity.organization_history_entity import OrganizationHistoryEntity
from src.domain.organization_history_domain import OrganizationHistoryDomain

def entity_to_domain(organization_history_entity: OrganizationHistoryEntity) -> OrganizationHistoryDomain:
    """
    (ORM 엔티티 → 도메인 객체 변환)
    ORM Entity를 도메인 객체로 변환합니다.
    Entity는 ORM(SQLAlchemy)에서 직접 사용하는 데이터베이스 모델이며,
    Domain은 비즈니스 로직을 수행하는 도메인 객체입니다.
    도메인 계층에서 데이터베이스 종속성을 줄이기 위해 Domain으로 변환하여 사용합니다.
    """
    return OrganizationHistoryDomain(
        seq=organization_history_entity.seq,
        organization_seq=organization_history_entity.organization_seq,
        action_type=organization_history_entity.action_type,
        before_value=organization_history_entity.before_value,
        after_value=organization_history_entity.after_value,
        username=organization_history_entity.username,
        created_at=organization_history_entity.created_at
    )

def domain_to_entity(organization_history_domain: OrganizationHistoryDomain) -> OrganizationHistoryEntity:
    """
    (도메인 객체 → ORM 엔티티 변환)
    Doamin 객체를 ORM Entity로 변환합니다.
    """
    return OrganizationHistoryEntity(
        organization_seq=organization_history_domain.organization_seq,
        action_type=organization_history_domain.action_type,
        before_value=organization_history_domain.before_value,
        after_value=organization_history_domain.after_value,
        username=organization_history_domain.username,
        created_at=organization_history_domain.created_at
    )
