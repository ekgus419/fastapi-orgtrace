from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from contextlib import suppress
import traceback
import json
from typing import Dict, Any

from src.dto.response.common_response_dto import CommonResponseDto
from src.logging.context.request_logging_context import RequestLoggingContext
from src.logging.extensions.structured_logging_adapter import StructuredLoggingAdapter


class ExceptionHandlerRegistry:
    """
    전역 예외 핸들러 등록 클래스

    FastAPI 애플리케이션에 공통적으로 사용할 예외 핸들러를 등록하며,
    요청별 컨텍스트 로거를 활용하여 구조화된 예외 로그를 출력합니다.
    """

    @classmethod
    def register(cls, app: FastAPI):
        """
        예외 핸들러를 FastAPI 앱에 등록합니다.

        Args:
            app: 예외 핸들러를 등록할 FastAPI 애플리케이션 인스턴스
        """
        app.add_exception_handler(HTTPException, cls.http_exception_handler)
        app.add_exception_handler(RequestValidationError, cls.validation_exception_handler)
        app.add_exception_handler(Exception, cls.global_exception_handler)


    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        HTTPException 예외를 처리합니다.

        Args:
            request: 발생한 요청 객체
            exc: 발생한 HTTPException 예외 객체

        Returns:
            JSON 형식의 HTTP 오류 응답
        """
        with suppress(LookupError):
            logger: StructuredLoggingAdapter = RequestLoggingContext.get()
            logger.start_structured(request.method, str(request.url.path), "http_exception_handler")

            input_data = await get_input_data(request)

            logger.exception_structured(
                message=exc.detail,
                exception=exc,
                context={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": exc.status_code,
                    "input": input_data or "[no input data]"
                }
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=CommonResponseDto(status="error", data=None, message=exc.detail).model_dump()
        )

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        RequestValidationError (입력 유효성 검증 오류) 예외를 처리합니다.

        Args:
            request: 발생한 요청 객체
            exc: 발생한 RequestValidationError 예외 객체

        Returns:
            유효성 검사 실패에 대한 응답 JSON
        """
        # 에러 메시지를 필드 경로 기반으로 재구성
        errors = {".".join(map(str, err.get("loc", []))): err.get("msg") for err in exc.errors()}

        input_data = await get_input_data(request)

        with suppress(LookupError):
            logger: StructuredLoggingAdapter = RequestLoggingContext.get()
            logger.start_structured(request.method, str(request.url.path), "validation_exception_handler")
            logger.exception_structured(
                message="유효성 검사 오류가 발생하였습니다.",
                cause=errors,
                exception=exc,
                context={
                    "method": request.method,
                    "path": str(request.url.path),
                    "input": input_data or "[no input data]",
                    # "errors": errors
                },
            )
        return JSONResponse(
            status_code=422,
            content=CommonResponseDto(status="fail", data=errors, message=None).model_dump()
        )

    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception):
        """
        기타 예상하지 못한 예외(500 Internal Server Error)를 처리합니다.

        Args:
            request: 발생한 요청 객체
            exc: 처리되지 않은 일반 예외 객체

        Returns:
            내부 서버 오류(500)에 대한 응답 JSON
        """
        logger = None
        with suppress(LookupError):
            logger = RequestLoggingContext.get()

        # 전체 traceback 문자열 생성
        traceback_str = traceback.format_exc()

        if logger:
            logger.start_structured(request.method, str(request.url.path), "global_exception_handler")
            logger.error_structured(
                message="Unhandled server error",
                context={
                    "method": request.method,
                    "path": str(request.url.path),
                    "client": request.client.host if request.client else None,
                    "traceback": traceback_str
                }
            )
        else:
            # 로깅 컨텍스트가 없을 경우 기본 출력
            print("[ERROR] Unhandled server error")
            print(traceback_str)

        return JSONResponse(
            status_code=500,
            content=CommonResponseDto(status="error", data=None, message="Internal Server Error").model_dump()
        )


async def get_input_data(request: Request) -> Dict[str, Any]:
    """
    요청 데이터에서 입력값(query, path, body)을 추출하여 반환합니다.

    Args:
        request: 요청 객체

    Returns:
        요청에서 추출한 모든 입력값을 담은 딕셔너리
    """
    input_data: Dict[str, Any] = {}

    # 쿼리 파라미터
    if request.query_params:
        input_data.update(dict(request.query_params))

    # path 파라미터
    if request.path_params:
        input_data.update(dict(request.path_params))

    # 요청 body (JSON)
    try:
        body_bytes = await request.body()
        if body_bytes:
            body_data = json.loads(body_bytes.decode("utf-8"))
            if isinstance(body_data, dict):
                input_data.update(body_data)
            else:
                input_data["body"] = body_data
    except Exception:
        input_data["body"] = "[Could not parse request body]"

    return input_data
