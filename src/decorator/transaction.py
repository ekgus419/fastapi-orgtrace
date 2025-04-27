import inspect
from functools import wraps
from sqlalchemy.orm import Session

def Transactional(func):
    """
    주입된 세션(db)을 기반으로 트랜잭션을 처리하는 데코레이터.
    - 반드시 외부에서 db가 주입되어야 하며,
    - 세션 생성은 FastAPI의 Depends(get_db)를 통해 수행되어야 합니다.

    Args:
        func (Callable): 트랜잭션 처리가 적용될 함수

    Returns:
        Callable: 트랜잭션을 적용한 함수
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        주어진 함수에서 트랜잭션을 적용하는 래퍼 함수입니다.

        주입된 DB 세션을 사용하여 트랜잭션을 처리합니다. 함수 실행 후
        정상적으로 실행되면 `commit()`을 호출하고, 예외가 발생하면
        `rollback()`을 호출하여 트랜잭션을 취소합니다.

        Args:
            *args: 원래 함수에 전달될 위치 인자
            **kwargs: 원래 함수에 전달될 키워드 인자

        Raises:
            ValueError: `db` 세션이 주입되지 않았을 경우 발생
            Exception: 함수 실행 중 예외가 발생하면 롤백 후 다시 발생

        Returns:
            Any: 원래 함수의 반환값
        """
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)

        db: Session = bound.arguments.get("db")

        if db is None:
            raise ValueError("트랜잭션을 적용하려면 db 세션이 주입되어야 합니다.")

        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise
    return wrapper
