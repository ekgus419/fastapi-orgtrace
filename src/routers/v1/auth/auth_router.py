from fastapi import Depends, status, Form
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.dto.request.auth.login_request_dto import LoginRequestDto
from src.dto.request.auth.refresh_token_request_dto import RefreshTokenRequestDto
from src.dto.request.auth.logout_request_dto import LogoutRequestDto
from src.dto.response.auth.token_response_dto import TokenResponseDto
from src.dto.response.common_response_dto import CommonResponseDto
from src.logging.api_logging_router import APILoggingRouter
from src.service.auth.auth_service import AuthService
from src.core.container import Container
from src.core.session import get_db

# 인증 관련 엔드포인트를 정의하는 APIRouter
router = APILoggingRouter()

@router.post("/swagger-token", status_code=status.HTTP_200_OK)
@inject
def swagger_login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """
    # 🔑 Swagger 전용 로그인 API (OAuth2 password flow 대응)

    FastAPI Swagger UI에서 Bearer 인증 연동을 위해,
    `access_token` + `token_type` 형식으로 응답을 반환합니다.

    ## 📝 Args:
    - **`username`** :
      - 로그인 아이디
    - **`password`** :
      - 로그인 패스워드
    - **`auth_service`** (`AuthService`):
      - 인증 서비스 **의존성 주입**

    ## 📤 Returns:
    - **발급된 Access Token 및 Token 타입 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 존재하지 않는 회원일 경우**`404 Not Found`** 오류 반환
      - 비밀번호가 일치하지 않을 경우 **`401 Bad request`** 오류 반환
    """
    access_token = auth_service.swagger_login(db, username, password)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/tokens", response_model=CommonResponseDto[TokenResponseDto], status_code=status.HTTP_200_OK)
@inject
def issue_tokens(
        payload: LoginRequestDto,
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """
    # 🔑 로그인 API (Access & Refresh Token 발급)

    회원의 인증 정보를 확인하고, **Access Token 및 Refresh Token**을 발급합니다.

    ## 📝 Args:
    - **`payload`** (`LoginRequestDto`):
      - 로그인 요청 데이터
      - **포함 필드:** `username`, `password`
    - **`auth_service`** (`AuthService`):
      - 인증 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[TokenResponseDto]`**
      - **발급된 Access Token 및 Refresh Token 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 존재하지 않는 회원일 경우**`404 Not Found`** 오류 반환
      - 비밀번호가 일치하지 않을 경우 **`401 Bad request`** 오류 반환
    """
    tokens = auth_service.login(db, payload)
    return CommonResponseDto(
        status="success",
        data=tokens,
        message=None
    )


@router.put("/tokens", response_model=CommonResponseDto[TokenResponseDto], status_code=status.HTTP_200_OK)
@inject
def refresh_access_token(
        payload: RefreshTokenRequestDto,
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """
    # 🔄 Refresh Token을 사용한 새로운 Access Token 발급 API

    유효한 **Refresh Token**을 제공하면 새로운 **Access Token**을 생성합니다.

    ## 📝 Args:
    - **`payload`** (`RefreshTokenRequestDto`):
      - **Refresh Token 요청 데이터**
    - **`auth_service`** (`AuthService`):
      - 인증 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[TokenResponseDto]`**
      - **새로운 Access Token 및 기존 Refresh Token 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 리프레시 토큰에 subject가 없을 경우**`401 Bad request`** 오류 반환
      - 존재하지 않는 회원일 경우**`404 Not Found`** 오류 반환
      - 리프레시 토큰이 유효하지 않거나 로그아웃한 회원인 경우 **`401 Bad request`** 오류 반환
    """
    tokens = auth_service.refresh_access_token(db, payload.refresh_token)
    return CommonResponseDto(
        status="success",
        data=tokens,
        message="Token refreshed successfully"
    )


@router.patch("/tokens", response_model=CommonResponseDto[None], status_code=status.HTTP_200_OK)
@inject
def revoke_tokens(
        payload: LogoutRequestDto,
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """
    # 🚪 로그아웃 API (Refresh Token 폐기)
    회원의 **Refresh Token**을 삭제하여 인증을 **무효화**합니다.

    ## 📝 Args:
    - **`payload`** (`LogoutRequestDto`):
      - 로그아웃 요청 데이터
      - **포함 필드:** `username`, `refresh_token`
    - **`auth_service`** (`AuthService`):
      - 인증 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[None]`**
      - **로그아웃 성공 메시지 반환**

     ## ⚠️ Raises:
    - **`HTTPException`**:
      - 존재하지 않는 회원일 경우**`404 Not Found`** 오류 반환
      - 리프레시 토큰이 일치하지 않을 경우 **`401 Bad request`** 오류 반환
    """
    auth_service.logout(db, payload)
    return CommonResponseDto(
        status="success",
        data=None,
        message="Logged out successfully"
    )
