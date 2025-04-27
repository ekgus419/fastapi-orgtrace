import logging
import json

from src.provider.time_provider import TimeProvider


class StructuredLoggingAdapter(logging.LoggerAdapter):
    """
    계층형 로그 출력을 위한 커스텀 StructuredLoggingAdapter.
    START / SQL / END / EXCEPTION / DEBUG 등을 블록 또는 구조화된 로그로 출력합니다.
    """

    def __init__(self, logger: logging.Logger, trace_id: str):
        """
        StructuredLoggingAdapter 초기화

        Args:
            logger (logging.Logger): 기본 로거 객체
            trace_id (str): 트레이스 ID (고유 식별자)
        """
        super().__init__(logger, {"trace_id": trace_id})
        self.trace_id = trace_id
        self._sql_logs: list[tuple[str, any]] = []  # SQL 로그를 누적 저장하는 리스트
        self._method  = ""  # HTTP 메서드
        self._path    = ""  # 요청 경로
        self._handler = ""  # 요청 처리 핸들러
        self._pending_tx_event = None  # 트랜잭션 로그 대기 상태

    def process(self, msg, kwargs):
        """
        LoggerAdapter의 기본 메서드로, 로그 메시지 출력 전에 `extra` 정보를 추가합니다.

        로그에 공통으로 포함되어야 하는 필드(trace_id, method, path, handler 등)를
        `kwargs["extra"]`에 삽입하여 로깅 포맷터 또는 핸들러에서 활용할 수 있도록 합니다.

        Args:
            msg (str): 로그 메시지 본문
            kwargs (dict): 로깅에 전달된 키워드 인수

        Returns:
            Tuple[str, dict]: 원본 메시지와 수정된 키워드 인수를 반환
        """
        kwargs["extra"] = kwargs.get("extra", {})
        kwargs["extra"].update({
            "trace_id": self.trace_id,
            "method": self._method,
            "path": self._path,
            "handler": self._handler,
        })
        return msg, kwargs

    def build_extra(self, log_type: str, *, message=None, cause=None, exception=None, context=None,
                    status_code=None, duration_ms=None, sql=None, time=None) -> dict:
        """
        구조화된 로그 출력을 위해 `extra` 필드를 구성합니다.

        이 메서드는 로그 종류(log_type)에 따라 부가 정보를 동적으로 포함시킵니다.
        이 정보는 JSON 로그 또는 파일 로거에 의해 직렬화되어 출력됩니다.

        Args:
            log_type (str): 로그의 타입 (예: START, END, EXCEPTION, DEBUG 등)
            message (str, optional): 로그 메시지
            cause (dict, optional): 상세 원인 메시지
            exception (Exception|str, optional): 예외 클래스 이름 또는 예외 메시지
            context (dict, optional): 추가적인 컨텍스트 정보
            status_code (int, optional): HTTP 상태 코드
            duration_ms (float, optional): 처리 시간 (밀리초 단위)
            sql (list, optional): 실행된 SQL 쿼리 목록
            time (str, optional): 로그 발생 시각 (포맷: YYYY-MM-DD HH:MM:SS). 지정하지 않으면 현재 시각 사용

        Returns:
            dict: 로그 출력을 위한 extra 딕셔너리
        """
        return {
            "trace_id": self.trace_id,
            "log_type": log_type,
            "method": self._method,
            "path": self._path,
            "handler": self._handler,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "time": time or TimeProvider.get_kst_now_str(),
            "log_message": message,
            "cause": cause,
            "exception": exception,
            "context": context,
            "sql": sql,
        }

    def clone_with_logger(self, new_logger: logging.Logger) -> "StructuredLoggingAdapter":
        """
        기존 StructuredLoggingAdapter의 상태를 복사해서,
        새로운 로거 인스턴스를 기반으로 새로운 Adapter를 생성합니다.

        Args:
            new_logger (logging.Logger): 새롭게 사용할 로거 인스턴스

        Returns:
            StructuredLoggingAdapter: 복제된 어댑터 인스턴스
        """
        clone = StructuredLoggingAdapter(new_logger, self.trace_id)
        clone._method = self._method
        clone._path = self._path
        clone._handler = self._handler
        return clone

    def start_structured(self, method: str, path: str, handler: str):
        """
        요청 시작 정보를 저장합니다. (메서드, 경로, 핸들러)

        Args:
            method (str): HTTP 요청 메서드 (GET, POST 등)
            path (str): 요청 URL 경로
            handler (str): 요청 처리 핸들러 이름
        """
        self._method = method
        self._path = path
        self._handler = handler or "unnamed_handler"

    def slow_sql_structured(self, query: str, params: any, elapsed: float) -> str:
        """
        슬로우 쿼리 전용 structured 로그 메시지를 반환합니다 (파일 출력용)

        Args:
            query (str): 실행된 SQL 쿼리
            params (any): SQL 파라미터
            elapsed (float): 쿼리 실행 시간 (밀리초 단위)

        Returns:
            str: 구조화된 슬로우 쿼리 로그 메시지
        """
        now = TimeProvider.get_kst_now_str()
        sql_section = self._format_sql_block(sql_logs=[(query, params)])

        formatted = self._format_block_full(
            log_type="SLOW_QUERY",
            method = self._method,
            path = self._path,
            handler =self._handler,
            elapsed=elapsed,
            query=sql_section,
            time=now
        )

        self.info(
            formatted,
            extra=self.build_extra(
                log_type="SLOW_QUERY",
                duration_ms=elapsed,
                sql=[{"query": query, "params": params}],
                time=now
            )
        )
        return formatted

    def sql_structured(self, query: str, params: any):
        """
        실행된 SQL 쿼리를 누적 저장합니다.

        Args:
            query (str): 실행된 SQL 쿼리
            params (any): SQL 파라미터
        """
        self._sql_logs.append((query, params))

    def end_structured(self, status_code: int, duration_ms: float):
        """
        요청 종료 시점에서 콘솔은 계층형 메시지, 파일(JSON)은 구조화된 JSON 로그를 출력합니다.

        Args:
            status_code (int): HTTP 상태 코드
            duration_ms (float): 요청 처리 시간 (밀리초 단위)
        """
        now = TimeProvider.get_kst_now_str()
        sql_section = self._format_sql_block()

        formatted_message = self._format_block_full(
            "START",
            status=status_code,
            duration_ms=duration_ms,
            time=now,
            query=sql_section
        )

        self.info(
            formatted_message,
            extra=self.build_extra(
                log_type="START",
                status_code=status_code,
                duration_ms=duration_ms,
                sql=[{"query": q, "params": p} for q, p in self._sql_logs],
                time=now
            )
        )

        # COMMIT / ROLLBACK 로그 출력 (END 이후)
        if self._pending_tx_event:
            _message = "✅ COMMIT" if self._pending_tx_event == "COMMIT" else "⛔️ ROLLBACK"
            formatted_message = self._format_block_full(
                    self._pending_tx_event,
                    message=_message
            )
            self.info(
                formatted_message,
                 extra=self.build_extra(
                     log_type=self._pending_tx_event,
                     message=_message
                 )
            )
            self._pending_tx_event = None

    def exception_structured(self, message: str, cause: dict = None, exception: Exception = None, context: dict = None):
        """
        계층형 예외 로그를 출력하는 메서드 (전역 예외 및 롤백 등).
        콘솔에는 메시지를 계층 구조로, JSON에는 구조화된 필드로 출력합니다.

        Args:
            message (str): 예외 메시지
            cause: 상세 원인 메시지
            exception (Exception, optional): 발생한 예외 객체
            context (dict, optional): 추가적인 컨텍스트 데이터
        """
        now = TimeProvider.get_kst_now_str()
        status_code    = context.get("status_code") if context else None
        exception_name = type(exception).__name__ if exception else None
        formatted_message = self._format_block_full(
            "EXCEPTION",
            message=message,
            cause=cause,
            exception=exception_name,
            context=context,
            status=status_code,
            time=now
        )
        self.error(
            formatted_message,
            extra=self.build_extra(
                log_type="EXCEPTION_STRUCTURED",
                message=message,
                cause=cause,
                exception=exception_name,
                context=context,
                status_code=status_code,
                time=now
            )
        )

    def error_structured(self, message: str, context: dict = None):
        """
        계층형 에러 로그를 출력하는 메서드.

        Args:
            message (str): 에러 메시지
            context (dict, optional): 추가적인 컨텍스트 데이터
        """
        now = TimeProvider.get_kst_now_str()
        status_code = context.get("status_code") if context else None
        formatted_message = self._format_block_full(
            "ERROR",
            message=message,
            context=context,
            status=status_code,
            time=now
        )
        self.error(
            formatted_message,
            extra=self.build_extra(
                log_type="ERROR_STRUCTURED",
                message=message,
                context=context,
                status_code=status_code,
                time=now
            )
        )

    def debug_structured(self, message: str, context: dict = None, method: str = "", path: str = "", handler: str = ""):
        """
        계층형 디버깅 로그를 출력하는 메서드.

        Args:
            message (str): 디버깅 메시지
            context (dict, optional): 추가적인 컨텍스트 데이터
            method (str, optional): HTTP 메서드
            path (str, optional): 요청 URL 경로
            handler (str, optional): 요청 처리 핸들러
        """
        now = TimeProvider.get_kst_now_str()
        formatted_message = self._format_block_full(
            "DEBUG",
            message=message,
            context=context,
            method=method,
            path=path,
            handler=handler,
            time=now
        )
        self.debug(
            formatted_message,
            extra=self.build_extra(
                log_type="DEBUG_STRUCTURED",
                message=message,
                context=context, time=now) | {"method": method, "path": path, "handler": handler}
        )

    def log_commit(self):
        """
        트랜잭션 커밋 로그
        """
        self._pending_tx_event = "COMMIT"

    def log_rollback(self):
        """
        트랜잭션 롤백 로그
        """
        self._pending_tx_event = "ROLLBACK"

    def _format_sql_block(self, sql_logs: list[tuple[str, any]] = None) -> str:
        """
        SQL 블록을 포매팅하여 출력합니다.

        Args:
            sql_logs (Optional): 직접 넘길 SQL 로그 리스트 (쿼리, 파라미터)

        Returns:
            str: 계층형 SQL 로그 텍스트
        """
        import sqlparse

        logs = sql_logs if sql_logs is not None else self._sql_logs

        if not logs:
            return "        [SQL] (None)"

        lines = []
        for query, params in logs:
            formatted = sqlparse.format(query, reindent=True, keyword_case="upper")
            sql_block = "\n".join(f"            {line}" for line in formatted.strip().splitlines())
            lines.append(f"        [SQL]\n{sql_block}\n            * Params: {params}")

        return "\n".join(lines)

    def _format_block_full(self, log_type: str, *, method: str = None, path: str = None, handler: str = None,
                           message: str = None, cause: dict = None, exception: str = None, status: int = None, context: dict = None,
                           time: str = None, elapsed: float = None, duration_ms: float = None,
                           query: str = None, params: any = None) -> str:
        """
        로그 타입에 따라 계층형 텍스트 블록 메시지를 구성하는 내부 메서드.

        이 메서드는 여러 가지 로그 정보를 받아서 보기 좋은 블록 형식으로 포맷된 문자열을 반환합니다.
        예를 들어, HTTP 요청에 대한 로그나 SQL 쿼리 로그 등을 포매팅하는 데 사용될 수 있습니다.

        Args:
            log_type (str): 로그 타입을 나타내는 문자열 (예: 'INFO', 'ERROR')
            method (str, optional): HTTP 메서드 (기본값은 객체의 _method 속성)
            path (str, optional): 요청된 경로 (기본값은 객체의 _path 속성)
            handler (str, optional): 핸들러 이름 (기본값은 객체의 _handler 속성)
            message (str, optional): 로그 메시지
            cause (dict, optional): 오류가 발생한 원인이나 상세 내용
            exception (str, optional): 예외 메시지
            status (int, optional): HTTP 상태 코드
            context (dict, optional): 추가적인 컨텍스트 정보 (예: 사용자 정보 등)
            time (str, optional): 로그의 시간 (기본값은 현재 시간)
            elapsed (float, optional): 경과 시간 (ms)
            duration_ms (float, optional): 처리 시간 (ms)
            query (str, optional): SQL 쿼리
            params (any, optional): SQL 쿼리 파라미터

        Returns:
            str: 계층형 구조로 포맷된 텍스트 로그 메시지
        """
        now = time or TimeProvider.get_kst_now_str()
        method = method or self._method
        path = path or self._path
        handler = handler or self._handler

        lines = [
            f"TraceId: {self.trace_id}",
            f"Method: {method}",
            f"Path: {path}",
            f"Handler: {handler}()"
        ]

        if status is not None:
            lines.append(f"Status: {status}")
        if message:
            lines.append(f"Message: {message}")
        if exception:
            lines.append(f"Exception: {exception}")
        if cause:
            lines.append(f"Cause: {json.dumps(cause, ensure_ascii=False)}")
        if context:
            lines.append(f"Context: {json.dumps(context, ensure_ascii=False)}")
        if elapsed is not None:
            lines.append(f"Elapsed: {elapsed:.2f}ms")
        if query:
            lines.append(f"Query:\n{query}")
        if params is not None:
            lines.append(f"Params: {params}")
        if duration_ms is not None:
            lines.append(f"Duration: {duration_ms:.2f}ms")

        lines.append(f"Time: {now}")
        body = "\n".join(f"    ▶ {line}" for line in lines)
        return f"──────────── [{log_type}]\n{body}\n──────────── [END]"
