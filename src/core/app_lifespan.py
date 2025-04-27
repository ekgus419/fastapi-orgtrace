from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from src.core.container import container

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    애플리케이션 시작 및 종료 시 실행할 리소스 초기화 및 정리
    FastAPI 애플리케이션의 lifespan 이벤트 핸들러.

    앱이 시작될 때 필요한 리소스를 초기화하고,
    종료 시 리소스를 정리하는 작업을 수행합니다.
    주로 DI 컨테이너 설정, 로깅 구성 등을 처리합니다.

    Args:
        app: FastAPI 애플리케이션 인스턴스

    Yields:
        None: 수명 주기 동안 컨텍스트를 유지
    """
    try:
        # 의존성 주입 컨테이너의 리소스를 초기화
        container.init_resources()

        # 지정된 패키지 내에서 의존성 주입 적용
        container.wire(packages=["src.routers"])

        # Uvicorn 로깅 설정 구성
        container.uvicorn_logger_config().configure()

        # lifespan 컨텍스트 유지
        yield

    except Exception as e:
        # 리소스 초기화 중 예외 발생 시 로그 출력 후 재발생
        print(f"Error during resource initialization: {e}")
        raise e

    finally:
        # 애플리케이션 종료 시 리소스 정리
        container.shutdown_resources()
