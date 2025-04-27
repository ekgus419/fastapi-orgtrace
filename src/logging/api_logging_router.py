from fastapi import APIRouter
from src.logging.logging_route_for_request_response import LoggingRouteForRequestResponse


class APILoggingRouter(APIRouter):
    """
    요청 및 응답에 대한 로깅이 자동으로 포함된 커스텀 APIRouter 클래스입니다.
    debug 모드가 아닐 경우, route_class를 LoggingRouteForRequestResponse로 설정하여
    모든 요청에 대해 로깅을 수행하도록 합니다.
    """

    def __init__(self, *args, debug: bool = False, **kwargs):
        """
        APILoggingRouter 생성자.

        Args:
            debug (bool): 디버그 모드 여부. True일 경우 로깅 비활성화.
            *args: 기타 APIRouter 인자.
            **kwargs: 기타 키워드 인자.
        """
        # 디버그 모드가 아닐 경우, 라우트 클래스에 로깅을 포함시킴
        if not debug:
            kwargs.setdefault("route_class", LoggingRouteForRequestResponse)

        # APIRouter 초기화
        super().__init__(*args, **kwargs)
