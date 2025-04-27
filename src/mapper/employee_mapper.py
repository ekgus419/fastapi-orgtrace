from src.domain.employee_domain import EmployeeDomain
from src.entity.employee_entity import EmployeeEntity

def entity_to_domain(employee_entity: EmployeeEntity) -> EmployeeDomain:
    """
    (ORM 엔티티 → 도메인 객체 변환)
    ORM Entity를 도메인 객체로 변환합니다.
    Entity는 ORM(SQLAlchemy)에서 직접 사용하는 데이터베이스 모델이며,
    Domain은 비즈니스 로직을 수행하는 도메인 객체입니다.
    도메인 계층에서 데이터베이스 종속성을 줄이기 위해 Domain으로 변환하여 사용합니다.
    """
    return EmployeeDomain(
        seq              = employee_entity.seq,
        position_seq     = employee_entity.position_seq,
        rank_seq         = employee_entity.rank_seq,
        organization_seq = employee_entity.organization_seq,
        status           = employee_entity.status,
        name             = employee_entity.name,
        email            = employee_entity.email,
        phone_number     = employee_entity.phone_number,
        extension_number = employee_entity.extension_number,
        hire_date        = employee_entity.hire_date,
        birth_date       = employee_entity.birth_date,
        incentive_yn     = employee_entity.incentive_yn,
        marketer_yn      = employee_entity.marketer_yn,
        created_at       = employee_entity.created_at,
        updated_at       = employee_entity.updated_at,
        deleted_at       = employee_entity.deleted_at,
    )

def domain_to_entity(employee_domain: EmployeeDomain) -> EmployeeEntity:
    """
    (도메인 객체 → ORM 엔티티 변환)
    Doamin 객체를 ORM Entity로 변환합니다.
    """
    return EmployeeEntity(
        position_seq     = employee_domain.position_seq,
        rank_seq         = employee_domain.rank_seq,
        organization_seq = employee_domain.organization_seq,
        status           = employee_domain.status,
        name             = employee_domain.name,
        email            = employee_domain.email,
        phone_number     = employee_domain.phone_number,
        extension_number = employee_domain.extension_number,
        hire_date        = employee_domain.hire_date,
        birth_date       = employee_domain.birth_date,
        incentive_yn     = employee_domain.incentive_yn,
        marketer_yn      = employee_domain.marketer_yn,
        created_at       = employee_domain.created_at,
        updated_at       = employee_domain.updated_at,
    )
