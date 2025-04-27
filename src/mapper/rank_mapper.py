from src.domain.rank_domain import RankDomain
from src.entity.rank_entity import RankEntity


def entity_to_domain(rank_entity: RankEntity) -> RankDomain:
    """
    (ORM 엔티티 → 도메인 객체 변환)
    ORM Entity를 도메인 객체로 변환합니다.
    Entity는 ORM(SQLAlchemy)에서 직접 사용하는 데이터베이스 모델이며,
    Domain은 비즈니스 로직을 수행하는 도메인 객체입니다.
    도메인 계층에서 데이터베이스 종속성을 줄이기 위해 Domain으로 변환하여 사용합니다.
    """
    return RankDomain(
        seq=rank_entity.seq,
        title=rank_entity.title,
        description=rank_entity.description,
        created_at=rank_entity.created_at,
        updated_at=rank_entity.updated_at,
        deleted_at=rank_entity.deleted_at,
    )


def domain_to_entity(rank_domain: RankDomain) -> RankEntity:
    """
    (도메인 객체 → ORM 엔티티 변환)
    Doamin 객체를 ORM Entity로 변환합니다.
    """
    return RankEntity(
        title=rank_domain.title,
        description=rank_domain.description,
    )
