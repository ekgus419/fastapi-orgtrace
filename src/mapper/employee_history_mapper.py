from src.entity.employee_history_entity import EmployeeHistoryEntity
from src.domain.employee_history_domain import EmployeeHistoryDomain

def entity_to_domain(employee_history_entity: EmployeeHistoryEntity) -> EmployeeHistoryDomain:
    """
    (ORM 엔티티 → 도메인 객체 변환)
    ORM Entity를 도메인 객체로 변환합니다.
    Entity는 ORM(SQLAlchemy)에서 직접 사용하는 데이터베이스 모델이며,
    Domain은 비즈니스 로직을 수행하는 도메인 객체입니다.
    도메인 계층에서 데이터베이스 종속성을 줄이기 위해 Domain으로 변환하여 사용합니다.
    """
    return EmployeeHistoryDomain(
        seq=employee_history_entity.seq,
        employee_seq=employee_history_entity.employee_seq,
        action_type=employee_history_entity.action_type,
        before_value=employee_history_entity.before_value,
        after_value=employee_history_entity.after_value,
        username=employee_history_entity.username,
        created_at=employee_history_entity.created_at
    )

def domain_to_entity(employee_history_domain: EmployeeHistoryDomain) -> EmployeeHistoryEntity:
    """
    (도메인 객체 → ORM 엔티티 변환)
    Doamin 객체를 ORM Entity로 변환합니다.
    """
    return EmployeeHistoryEntity(
        employee_seq=employee_history_domain.employee_seq,
        action_type=employee_history_domain.action_type,
        before_value=employee_history_domain.before_value,
        after_value=employee_history_domain.after_value,
        username=employee_history_domain.username,
        created_at=employee_history_domain.created_at
    )
