from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """
    FastAPI 앱에 CORS(Cross-Origin Resource Sharing) 미들웨어를 설정합니다.

    프론트엔드와 백엔드가 서로 다른 출처(도메인 또는 포트)에서 실행될 경우,
    브라우저의 보안 정책에 의해 API 요청이 차단되는 것을 방지합니다.

    개발 환경에서는 로컬 서버 간의 통신을 허용하기 위해 사용되며,
    배포 시에는 실제 서비스 도메인에 맞게 origins를 변경해야 합니다.

    Args:
        app: CORS 미들웨어를 적용할 FastAPI 애플리케이션 인스턴스
    """
    origins = [
        "http://localhost:8000",  # Next.js 개발 서버 (프론트엔드 개발 환경)
        "http://127.0.0.1:8001",  # Swagger UI 또는 다른 로컬 도구에서 호출할 수 있는 주소
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,     # 지정한 origin에서의 요청만 허용
        allow_credentials=True,    # 쿠키, 인증 정보 포함한 요청 허용
        allow_methods=["*"],       # 모든 HTTP 메서드 허용 (GET, POST 등)
        allow_headers=["*"],       # 모든 HTTP 헤더 허용
    )
