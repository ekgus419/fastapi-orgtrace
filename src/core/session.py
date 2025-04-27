from sqlalchemy.orm import Session
from src.core.database import SessionLocal

def get_db() -> Session:
    """
    요청당 하나의 DB 세션을 생성하고, 요청이 끝나면 세션을 종료합니다.

    이 함수는 FastAPI의 의존성 주입 시스템에서 사용됩니다.
    `yield`를 통해 세션을 반환하고, 요청이 끝난 후 `finally` 블록에서 세션을 안전하게 닫습니다.

    Yields:
        Session: 데이터베이스 세션 객체
    """
    db = SessionLocal()
    try:
        yield db  # 호출자에게 세션을 제공
    finally:
        db.close()  # 요청이 끝난 후 세션 종료
