from fastapi import Request

from src.core.session import get_db
import logging

from src.logging.api_logging_router import APILoggingRouter
from src.logging.config.logging_config import LoggingConfig
from src.logging.extensions.structured_logging_adapter import StructuredLoggingAdapter
from src.logging.context.request_logging_context import RequestLoggingContext
import uuid
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session


# router = APILoggingRouter(debug=True) # DEBUG 로그만 나옴
router = APILoggingRouter() # DEBUG 로그 + API 요청 로그

@router.get("/test-debug")
async def test_debug(request: Request):
    trace_id = str(uuid.uuid4())
    # 도메인 설정
    base_logger = LoggingConfig().get_logger("rank")

    # 로거 및 핸들러 레벨 설정
    base_logger.setLevel(logging.DEBUG)
    for handler in base_logger.handlers:
        handler.setLevel(logging.DEBUG)

    logger = StructuredLoggingAdapter(base_logger, trace_id)
    RequestLoggingContext.set(logger)
    logger.debug_structured(
        message="🐛 테스트 로그",
        context={"active": True},
        method=request.method,
        path=str(request.url.path),
        handler=test_debug.__name__
    )

    return {"message": "ok"}

@router.get("/test/slow-sql")
def test_slow_sql(db: Session = Depends(get_db)):
    """
    슬로우 쿼리 테스트용 API

    - 쿼리 실행 시간이 1초를 초과하면 structured 슬로우 쿼리 로그가 남음
    """
    db.execute(text("SELECT SLEEP(1.5)"))  # MySQL 기준. 1.5초 지연 쿼리
    return {"status": "ok"}

@router.get("/zero-division")
def force_zero_division():
    return 1 / 0
