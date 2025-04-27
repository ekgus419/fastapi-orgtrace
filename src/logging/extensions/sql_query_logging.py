import time
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine


from src.core.settings import settings
from src.logging.context.request_logging_context import RequestLoggingContext
from src.logging.extensions.structured_logging_adapter import StructuredLoggingAdapter


class SqlQueryLogging:
    """
    SQL 쿼리 로깅을 설정하는 클래스입니다.

    - SQLAlchemy 엔진에 이벤트 리스너를 등록하여 쿼리 실행 전후에 로깅합니다.
    - 실행 시간을 계산하여 Slow 쿼리는 별도로 slow query 로그 파일에 기록합니다.
    - `RequestLoggingContext`를 통해 각 요청에 대한 로그를 추적합니다.
    """

    def __init__(self, slow_threshold: float = None):
        """
        SQL 로거를 설정합니다.

        실행 환경에 따라 slow 쿼리의 기준 시간을 설정합니다.
        - 프로덕션 환경: 1.0초
        - 다른 환경: 0.5초

        Args:
            slow_threshold (float): slow 쿼리 임계 시간 (초 단위)
        """
        self.slow_threshold = settings.SLOW_QUERY_THRESHOLD
        self.slow_logger = None  # lazy init

    def register_listeners(self, engine: Engine):
        """
        SQLAlchemy 엔진에 SQL 실행 전후에 동작할 이벤트 리스너를 등록합니다.

        Args:
            engine (Engine): SQLAlchemy 엔진 객체
        """
        event.listen(engine, "before_cursor_execute", self.before_cursor_execute)
        event.listen(engine, "after_cursor_execute", self.after_cursor_execute)

    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """
        SQL 쿼리 실행 전, 쿼리와 파라미터를 로깅하고, 시작 시간을 기록합니다.

        - 로그 대상 쿼리: SELECT, INSERT, UPDATE, DELETE 등 모든 쿼리
        - 출력 내용: SQL 쿼리문, 바인딩된 파라미터 값
        - 로그는 RequestLoggingContext에서 저장된 도메인별 로거로 기록됩니다.

        Args:
            conn: SQL 커넥션 객체
            cursor: SQL 커서 객체
            statement: 실행될 SQL 문장
            parameters: SQL 바인딩 파라미터
            context: 실행 컨텍스트
            executemany: 여러 번 실행 여부
        """
        context._query_start_time = time.time()

        try:
            logger: StructuredLoggingAdapter = RequestLoggingContext.get()
            if hasattr(logger, "sql_structured"):
                if executemany:
                    # 다중 쿼리 실행의 경우 각 파라미터 셋에 대해 로그 기록
                    for param_set in parameters:
                        logger.sql_structured(query=statement, params=param_set)
                else:
                    logger.sql_structured(query=statement, params=parameters)

        except LookupError:
            # RequestLoggingContext가 없는 경우 (예: 초기 쿼리) 로깅을 생략
            pass

    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """
        SQL 쿼리 실행 후, 실행 시간을 계산하고 slow 쿼리 여부를 확인하여 로깅합니다.

        - 로그 대상 쿼리: SELECT, INSERT, UPDATE, DELETE 등 모든 쿼리
        - 출력 조건: 실행 시간이 slow_threshold를 초과할 경우
        - 출력 내용: slow 쿼리 실행 시간, 쿼리문, 바인딩된 파라미터 값

        Args:
            conn: SQL 커넥션 객체
            cursor: SQL 커서 객체
            statement: 실행된 SQL 문장
            parameters: SQL 바인딩 파라미터
            context: 실행 컨텍스트
            executemany: 여러 번 실행 여부
        """
        duration = time.time() - getattr(context, "_query_start_time", time.time())

        if duration >= self.slow_threshold:
            self._log_slow_query(statement, parameters, round(duration * 1000, 2))

    def _log_slow_query(self, statement, parameters, duration_ms):
        """
        Slow 쿼리의 실행 시간을 기록하고, slow query 로그 파일에 경고 메시지를 추가합니다.

        Args:
            statement: 실행된 SQL 문장
            parameters: SQL 바인딩 파라미터
            duration_ms: 실행 시간 (밀리초)
        """
        try:
            # 슬로우 로거를 컨텍스트에서 가져옴 (clone_with_logger 로 복제된 상태여야 함)
            slow_logger = RequestLoggingContext.get_slow()
            slow_logger.slow_sql_structured(statement, parameters, duration_ms)
        except LookupError:
            # 요청 컨텍스트 외부일 경우 fallback 로거 사용
            from src.core.container import container
            trace_id = "unknown"
            dummy_logger = StructuredLoggingAdapter(
                logger=container.logger_config().get_logger("slow_query"),
                trace_id=trace_id
            )
            dummy_logger.slow_sql_structured(statement, parameters, duration_ms)

    def register_session_listeners(self, session_factory: sessionmaker):
        """
        Session의 커밋 및 롤백 후 실행될 이벤트 리스너를 등록합니다.

        Args:
            session_factory (sessionmaker): SQLAlchemy 세션 팩토리 객체
        """
        event.listen(session_factory, "after_commit", self.after_commit)
        event.listen(session_factory, "after_rollback", self.after_rollback)

    def after_commit(self, session: Session):
        """
        세션 커밋 후, 트랜잭션이 성공적으로 완료되었음을 RequestLoggingContext에 기록합니다.
        - 출력 내용: "✅ COMMIT"
        """
        self._log_tx_event("commit")

    def after_rollback(self, session: Session):
        """
        세션 롤백 후, 트랜잭션 오류를 RequestLoggingContext에 기록합니다.
        - 출력 내용: "⛔️ ROLLBACK"
        """
        self._log_tx_event("rollback")

    def _log_tx_event(self, event_type: str):
        """
        트랜잭션 이벤트(COMMIT/ROLLBACK)를 로깅합니다.

        Args:
            event_type (str): 트랜잭션 이벤트 유형 (commit/rollback)
        """
        try:
            logger: StructuredLoggingAdapter = RequestLoggingContext.get()
            if event_type == "commit" and hasattr(logger, "log_commit"):
                logger.log_commit()
            elif event_type == "rollback" and hasattr(logger, "log_rollback"):
                logger.log_rollback()
        except LookupError:
            pass
