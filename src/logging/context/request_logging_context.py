from src.logging.extensions.structured_logging_adapter import StructuredLoggingAdapter
from contextvars import ContextVar
import logging


class RequestLoggingContext:
    """
    요청 단위로 logger와 trace_id를 안전하게 보관하고 접근할 수 있도록 해주는 컨텍스트 클래스입니다.
    contextvars를 활용하여 각 요청별로 독립된 상태를 유지합니다.
    """

    # 요청 스코프 logger와 trace_id를 저장하는 context 변수
    _logger_var: ContextVar[logging.Logger] = ContextVar("request_logger")
    _slow_logger_var: ContextVar[StructuredLoggingAdapter] = ContextVar("slow_logger")
    _trace_id_var: ContextVar[str] = ContextVar("trace_id")

    @classmethod
    def set(cls, logger: logging.Logger, trace_id: str = None):
        """
        요청 컨텍스트에 logger와 trace_id를 설정합니다.
        trace_id가 전달되지 않으면 자동으로 UUID를 생성합니다.

        Args:
            logger (logging.Logger): 요청별 로거 인스턴스
            trace_id (str, optional): 요청 추적용 trace_id (미지정 시 자동 생성)
        """
        import uuid
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        cls._logger_var.set(logger)
        cls._trace_id_var.set(trace_id)

    @classmethod
    def set_slow(cls, logger: logging.Logger, trace_id: str = None):
        """
        요청 컨텍스트에 logger와 trace_id를 설정합니다.
        trace_id가 전달되지 않으면 자동으로 UUID를 생성합니다.

        Args:
            logger (logging.Logger): 요청별 로거 인스턴스
            trace_id (str, optional): 요청 추적용 trace_id (미지정 시 자동 생성)
        """
        import uuid
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        cls._slow_logger_var.set(logger)
        cls._trace_id_var.set(trace_id)

    @classmethod
    def get_slow(cls) -> StructuredLoggingAdapter:
        return cls._slow_logger_var.get()

    @classmethod
    def get(cls) -> StructuredLoggingAdapter:
        """
        현재 컨텍스트에 설정된 logger를 반환합니다.

        Returns:
            StructuredLoggingAdapter: 현재 요청에 연결된 로거 어댑터
        """
        return cls._logger_var.get()

    @classmethod
    def get_trace_id(cls) -> str:
        """
        현재 요청의 trace_id를 반환합니다.
        trace_id가 없을 경우 "None" 문자열을 반환합니다.

        Returns:
            str: trace_id 문자열
        """
        try:
            return cls._trace_id_var.get()
        except LookupError:
            return "None"

    @classmethod
    def clear(cls) -> None:
        """
        요청 컨텍스트를 초기화합니다.
        기본 로거와 새로운 trace_id를 설정합니다.
        (예: 요청 스코프가 사라졌거나 예외 발생 후 복구 상황)
        """
        from src.logging.config.logging_config import LoggingConfig
        import uuid

        trace_id = str(uuid.uuid4())[:8]  # 간단한 trace_id 생성
        base_logger = LoggingConfig().get_logger("default")
        default_logger = StructuredLoggingAdapter(base_logger, trace_id)

        cls._logger_var.set(default_logger)
        cls._trace_id_var.set(trace_id)
