import logging
from src.logging.context.request_logging_context import RequestLoggingContext


class ConsoleLogColors:
    """
    콘솔 로그 출력 시 사용할 ANSI 색상 코드 정의 클래스입니다.
    각 로그 레벨에 대응하는 색상을 설정합니다.
    """
    DEBUG = "\033[95m"      # 보라
    INFO = "\033[92m"       # 초록
    WARNING = "\033[93m"    # 노랑
    ERROR = "\033[91m"      # 빨강
    CRITICAL = "\033[95m"   # 마젠타
    RESET = "\033[0m"       # 색상 초기화



class ConsoleLogFormatter(logging.Formatter):
    """
    콘솔 로그 출력 형식을 정의하는 포매터 클래스입니다.
    로그 메시지 앞에 색상을 적용하고, trace_id 정보를 부여합니다.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        로그 레코드를 포매팅합니다.

        Args:
            record (logging.LogRecord): 로그 레코드 객체

        Returns:
            str: 포매팅된 문자열 로그 메시지
        """
        try:
            # 현재 요청의 trace_id를 로그 레코드에 포함
            record.trace_id = RequestLoggingContext.get_trace_id()
        except Exception:
            record.trace_id = "unknown"

        # 로그 레벨에 해당하는 색상 적용
        level_color = getattr(ConsoleLogColors, record.levelname.upper(), "")
        reset = ConsoleLogColors.RESET

        return f"{level_color}{record.getMessage()}{reset}"


def get_console_log_formatter() -> logging.Formatter:
    """
    콘솔 로그 출력을 위한 포매터 인스턴스를 반환합니다.

    Returns:
        logging.Formatter: ConsoleLogFormatter 인스턴스
    """
    return ConsoleLogFormatter()
