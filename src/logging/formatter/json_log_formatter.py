
from pythonjsonlogger.json import JsonFormatter
from src.logging.context.request_logging_context import RequestLoggingContext
import json
import logging


class JsonLogFormatter(JsonFormatter):
    """
    로그 메시지를 JSON 형식으로 포매팅하는 커스텀 포매터입니다.
    요청별 trace_id를 포함하며, 필요한 필드만 추출해 출력합니다.
    """

    @staticmethod
    def safe_default(obj):
        """
        JSON 직렬화가 어려운 객체를 안전하게 문자열로 변환합니다.

        - datetime 객체는 ISO 8601 문자열로 변환
        - 그 외 객체는 str()을 통해 문자열로 변환

        이는 로그를 JSON 형태로 출력할 때 발생할 수 있는 직렬화 오류를 방지하기 위한 유틸리티입니다.

        Args:
            obj (Any): 직렬화 대상 객체

        Returns:
            str: 직렬화 가능한 문자열 표현
        """
        from datetime import datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    @staticmethod
    def clean_sql(sql):
        """
        SQL 로그 데이터를 정리합니다.
        - SQL 리스트 내부의 쿼리문에서 줄바꿈 문자를 제거하고 trim 처리합니다.
        - 각 쿼리와 파라미터를 구조화된 딕셔너리로 재구성합니다.

        Args:
            sql (list[dict] | any): SQL 로그 데이터 (리스트 형태가 아닐 경우 그대로 반환)

        Returns:
            list[dict]: 정제된 SQL 로그 리스트
        """
        if not isinstance(sql, list):
            return sql
        cleaned = []
        for item in sql:
            query = item.get("query", "")
            params = item.get("params", [])
            query = query.replace("\\n", " ").replace("\n", " ").strip()
            cleaned.append({"query": query, "params": params})
        return cleaned

    def format(self, record: logging.LogRecord) -> str:
        """
        로그 레코드를 JSON 문자열로 포매팅합니다.

        Args:
            record (logging.LogRecord): 로그 레코드 객체.

        Returns:
            str: JSON 형식의 로그 문자열.
        """
        # 특정 log_type이 "END"인 경우 로그를 출력하지 않음 (예: 요청 종료 표시 용도)
        if getattr(record, "log_type", "") == "END":
            return ""

        log_record = self._build_log_record(record)

        if not log_record.get("trace_id"):
            try:
                # 현재 요청에 대한 trace_id 삽입
                log_record["trace_id"] = RequestLoggingContext.get_trace_id()
            except Exception:
                log_record["trace_id"] = "unknown"

        return json.dumps(
            {k: v for k, v in log_record.items() if v is not None},
            ensure_ascii=False,
            default=self.safe_default
        )


    def _build_log_record(self, record: logging.LogRecord) -> dict:
        """
        로그 레코드에서 주요 정보를 추출하여 딕셔너리 형태로 구성합니다.

        Args:
            record (logging.LogRecord): 로그 레코드 객체.

        Returns:
            dict: 로그 필드 정보를 담은 딕셔너리.
        """
        from datetime import datetime
        time_value = getattr(record, "time", None)
        return {
            "trace_id": getattr(record, "trace_id", None),
            "log_type": getattr(record, "log_type", None),
            "level": record.levelname,
            "time": time_value.isoformat() if isinstance(time_value, datetime) else time_value,
            "name": record.name,
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "handler": getattr(record, "handler", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "message": getattr(record, "log_message", None),
            "exception": getattr(record, "exception", None),
            "context": getattr(record, "context", None),
            "sql": self.clean_sql(getattr(record, "sql", None)),
        }


def get_json_log_formatter() -> JsonLogFormatter:
    """
    JSON 포맷 로그 출력을 위한 JsonLogFormatter 인스턴스를 반환합니다.

    Returns:
        JsonLogFormatter: JSON 로그 포매터 인스턴스.
    """
    return JsonLogFormatter()
