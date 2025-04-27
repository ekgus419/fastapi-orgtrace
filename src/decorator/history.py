import json
import importlib
import inspect
from functools import wraps
from sqlalchemy.orm import Session

from src.provider.history_provider import HistoryProvider
from src.provider.time_provider import TimeProvider


def History(entity: str, action: str):
    """
    AOP 방식으로 히스토리를 자동 기록하는 데코레이터입니다.

    서비스 함수에 아래와 같은 방식으로 사용합니다:
        @History(entity="employee", action="UPDATE")

    동작 설명:
        - 서비스 함수 실행 전후의 상태를 비교하여 히스토리 저장
        - INSERT, UPDATE, DELETE 액션을 기준으로 상태 추적
        - before/after 값을 JSON 문자열로 저장
        - 동적으로 도메인 및 매퍼 로딩

    주의사항:
        - 외부에서 SQLAlchemy 세션(`db`)이 반드시 주입되어야 합니다 (예: get_db)
        - 이 데코레이터는 자체적으로 세션을 생성하거나 종료하지 않습니다

    Args:
        entity (str): 대상 엔터티 이름 (예: "employee")
        action (str): 수행되는 작업 유형 ("INSERT", "UPDATE", "DELETE")

    Returns:
        Callable: 데코레이터 함수
    """

    def decorator(func):
        """
        History는 entity와 action이라는 파라미터를 받아서,
        실제로 히스토리를 기록하는 wrapper 함수를 반환합니다. (동적으로 wrapper를 생성)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            원래의 서비스 함수를 감싸서 히스토리를 기록하는 래퍼 함수입니다.

            주입된 `db` 세션을 통해 before/after 상태를 조회 및 기록하며,
            필요한 경우 히스토리 레코드를 동적으로 생성하여 저장합니다.

            Raises:
                ValueError: `db` 세션이 주입되지 않은 경우 예외 발생

            Returns:
                Any: 원래 서비스 함수의 반환값
            """
            from src.core.container import container

            # 함수 시그니처 분석
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            db: Session = bound.arguments.get("db")
            if db is None:
                raise ValueError("히스토리 저장을 위해서는 db 세션이 주입되어야 합니다.")

            username = kwargs.get("username")

            # 서비스 함수의 시그니처 분석 (인자명 기반으로 entity_seq 추출)
            param_names = list(sig.parameters.keys())

            # 1. entity_seq 추출
            entity_seq = HistoryProvider.extract_entity_seq(entity, args, kwargs, param_names)

            repo = getattr(container, f"{entity}_repository")()

            # 2. before 상태 조회 (INSERT 제외)
            before_dict = after_dict = None
            if action != "INSERT" and entity_seq:
                before_entity = getattr(repo, f"get_{entity}_by_seq")(db, entity_seq)
                if before_entity:
                    before_dict = HistoryProvider.clean_dict(before_entity.__dict__.copy())

            # 3. 서비스 함수 실행
            result = func(*args, **kwargs)

            # 4. after 상태 추출
            if action == "DELETE":
                target_seq = entity_seq
            else:
                after_dict = HistoryProvider.clean_dict(result.__dict__.copy())
                target_seq = result.seq

            # 5. 도메인 및 매퍼 동적 로딩
            domain_module = importlib.import_module(f"src.domain.{entity}_history_domain")
            mapper_module = importlib.import_module(f"src.mapper.{entity}_history_mapper")
            DomainClass = getattr(domain_module, f"{entity.capitalize()}HistoryDomain")
            domain_to_entity = getattr(mapper_module, "domain_to_entity")

            # 6. 도메인 객체 생성
            domain = DomainClass(
                **{
                    f"{entity}_seq": target_seq,
                    "action_type": action,
                    "before_value": json.dumps(before_dict, default=str, sort_keys=True) if before_dict else None,
                    "after_value": json.dumps(after_dict, default=str, sort_keys=True) if after_dict else None,
                    "username": username,
                    "created_at": TimeProvider.get_kst_now(),
                }
            )

            # 7. 히스토리 저장
            history_repo = getattr(container, f"{entity}_history_repository")()
            history_repo.save_history(db=db, domain_obj=domain, domain_to_entity=domain_to_entity)

            return result

        return wrapper

    return decorator