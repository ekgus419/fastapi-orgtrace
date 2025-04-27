from fastapi.routing import APIRoute
from fastapi.requests import Request
from fastapi.responses import Response
import time
import uuid

from src.logging.config.logging_config import LoggingConfig
from src.logging.context.request_logging_context import RequestLoggingContext
from src.provider.logging_router_provider import LoggingRouterProvider
from src.logging.extensions.structured_logging_adapter import StructuredLoggingAdapter


class LoggingRouteForRequestResponse(APIRoute):
    """
    요청 및 응답 정보를 구조화 로그로 기록하는 커스텀 FastAPI APIRoute 클래스입니다.

    - 요청 시작 시 START 로그를 출력하고,
    - 요청 종료 시 END 로그를 출력합니다.
    - 로그에는 trace_id, HTTP 메서드, 경로, 핸들러, 응답 상태 코드, 처리 시간(ms) 등이 포함됩니다.
    """

    def get_route_handler(self):
        # 기존 라우트 핸들러 가져오기
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Response:
            # 의존성 주입 컨테이너
            from src.core.container import container

            logging_router_provider = LoggingRouterProvider()

            # 요청 시작 시간
            start_time = time.time()
            # 짧은 trace_id 생성
            trace_id = str(uuid.uuid4())[:8]

            # 요청 경로로부터 도메인 추출 (ex: "/user/login" → "user")
            domain = logging_router_provider.extract_domain_from_path(str(request.url.path))

            # 엔드포인트 함수 이름 추출
            handler_name = logging_router_provider.resolve_handler_name(self.endpoint)

            # 도메인별 로거 설정 및 trace_id 포함한 StructuredLogger 생성
            logger_config: LoggingConfig = container.logger_config()

            logger = StructuredLoggingAdapter(logger_config.get_logger(domain), trace_id)
            slow_logger = logger.clone_with_logger(logger_config.get_logger("slow_query"))

            # 요청 컨텍스트에 로거 설정
            RequestLoggingContext.set(logger)
            RequestLoggingContext.set_slow(slow_logger)

            # START 로그 세팅
            logger.start_structured(method=request.method, path=str(request.url.path), handler=handler_name)
            slow_logger.start_structured(method=request.method, path=str(request.url.path), handler=handler_name)

            try:
                response = await original_handler(request)
                # 응답 헤더에 trace_id 추가 (프론트엔드에서 추적 가능)
                response.headers["X-Trace-Id"] = trace_id
            except Exception as exc:
                # 예외 발생 시 로깅 처리 추가 가능
                raise

            # 처리 시간(ms) 계산
            duration = (time.time() - start_time) * 1000

            # END 로그 출력
            logger.end_structured(status_code=response.status_code, duration_ms=round(duration, 2))

            return response
        return custom_handler
