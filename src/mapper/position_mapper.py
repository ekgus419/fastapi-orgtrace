from src.entity.position_entity import PositionEntity
from src.domain.position_domain import PositionDomain
from src.dto.request.position.position_update_request_dto import PositionUpdateRequestDto

def entity_to_domain(position_entity: PositionEntity) -> PositionDomain:
    """
    (ORM 엔티티 → 도메인 객체 변환)
    ORM Entity를 도메인 객체로 변환합니다.
    Entity는 ORM(SQLAlchemy)에서 직접 사용하는 데이터베이스 모델이며,
    Domain은 비즈니스 로직을 수행하는 도메인 객체입니다.
    도메인 계층에서 데이터베이스 종속성을 줄이기 위해 Domain으로 변환하여 사용합니다.
    """
    return PositionDomain(
        seq=position_entity.seq,
        title=position_entity.title,
        role_seq=position_entity.role_seq,
        description=position_entity.description,
        created_at=position_entity.created_at,
        updated_at=position_entity.updated_at,
        deleted_at=position_entity.deleted_at,
    )

def domain_to_entity(position_domain: PositionDomain) -> PositionEntity:
    """
    (도메인 객체 → ORM 엔티티 변환)
    Doamin 객체를 ORM Entity로 변환합니다.
    """
    return PositionEntity(
        title=position_domain.title,
        role_seq=position_domain.role_seq,
        description=position_domain.description,
    )
