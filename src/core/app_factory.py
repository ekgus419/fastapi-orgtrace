from fastapi import FastAPI
from src.core.app_lifespan import lifespan
from src.middleware.cors_middleware import setup_cors
from src.exception.exception_handler_registry import ExceptionHandlerRegistry
from src.routers.v1.router_binder import register_routers

def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션을 생성하고 설정을 초기화합니다.

    - lifespan 설정을 통해 앱 시작/종료 시 실행될 로직을 지정합니다.
    - CORS, 예외 핸들러, 라우터 등 앱의 핵심 설정들을 구성합니다.

    Returns:
        설정이 완료된 FastAPI 앱 인스턴스
    """

    # 앱 생성 시 생명주기 관리 설정
    app = FastAPI(lifespan=lifespan)

    # CORS 미들웨어 등록 (프론트엔드와의 연동 허용)
    setup_cors(app)

    # 공통 예외 핸들러 등록 (HTTPException, ValidationError 등 처리)
    ExceptionHandlerRegistry.register(app)

    # API 라우터 등록 (v1 기준 도메인별 라우팅 구성)
    register_routers(app)

    return app
