import logging
from src.logging.context.request_logging_context import RequestLoggingContext


class TextLogFormatter(logging.Formatter):
    """
    로그 메시지를 텍스트 형식으로 포매팅하는 커스텀 포매터입니다.
    요청별 trace_id를 포함하며, 필요한 필드만 추출해 출력합니다.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        로그 레코드를 텍스트 형태로 포매팅합니다.

        Args:
            record (logging.LogRecord): 로그 레코드 객체.

        Returns:
            str: 메시지 문자열만 반환 (추가 포매팅 없음).
        """
        # trace_id가 없을 경우, 컨텍스트에서 가져와 추가
        if not hasattr(record, "trace_id"):
            record.trace_id = RequestLoggingContext.get_trace_id()

        # 메시지 그대로 반환 (추가 포맷 없음)
        return record.getMessage()


def get_text_log_formatter() -> logging.Formatter:
    """
    텍스트 형태의 로그 출력을 위한 포매터 인스턴스를 반환합니다.

    Returns:
        logging.Formatter: TextLogFormatter 인스턴스.
    """
    return TextLogFormatter()
