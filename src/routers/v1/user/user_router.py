from fastapi import Depends, Query, status
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.session import get_db
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.logging.api_logging_router import APILoggingRouter
from src.service.user.user_service import UserService
from src.dto.request.user.user_create_request_dto import UserCreateRequestDto
from src.dto.request.user.password_update_request_dto import PasswordUpdateRequestDto
from src.dto.response.user.user_response_dto import UserResponseDto
from src.dto.response.common_response_dto import CommonResponseDto

# 회원 관리 관련 API 엔드포인트를 정의하는 APIRouter
# router = APIRouter(
#     # dependencies=[Depends(get_current_username)]  # 인증이 필요할 경우 활성화
# )
router = APILoggingRouter()

@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[UserResponseDto]])
@inject
def get_users(
        page: int = Query(1, ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'username')"),
        order: str = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        db: Session = Depends(get_db),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """
    # 📌 회원 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 회원 수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'username'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`user_service`** (`UserService`): 회원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[UserResponseDto]]`**
      회원 목록과 페이지네이션 정보 반환
    """
    users, total_count = user_service.get_users(db, page, size, sort_by, order)
    user_responses = [UserResponseDto.model_validate(e) for e in users]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=user_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )


@router.get("/{user_seq}", response_model=CommonResponseDto[UserResponseDto])
@inject
def get_user(
        user_seq: int,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """
    # 🔍 특정 회원 조회 API

    ## 📝 Args:
    - **`user_seq`** (`int`): 조회할 회원 **ID**
    - **`user_service`** (`UserService`): 회원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[UserResponseDto]`**
      조회된 **회원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 회원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    user = user_service.get_user_by_seq(db, user_seq)
    return CommonResponseDto(status="success", data=user, message=None)


@router.post("/", response_model=CommonResponseDto[UserResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_user(
        user_create_request_dto: UserCreateRequestDto,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """
    # 🆕 새 회원 생성 API

    ## 📝 Args:
    - **`user_create_request_dto`** (`UserCreateRequestDto`):
      - 회원 생성 요청 데이터
      - **포함 필드:** `username`, `email`, `password`
    - **`user_service`** (`UserService`):
      - 회원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[UserResponseDto]`**
      - 생성된 **회원 정보 반환**
    """
    user = user_service.create_user(db, user_create_request=user_create_request_dto)
    return CommonResponseDto(status="success", data=user, message="User created successfully")


@router.patch("/{user_seq}/password", response_model=CommonResponseDto[UserResponseDto], status_code=status.HTTP_200_OK)
@inject
def update_password(
        user_seq: int,
        password_update_request_dto: PasswordUpdateRequestDto,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """
    # 🔐 특정 회원의 비밀번호 변경 API

    ## 📝 Args:
    - **`user_seq`** (`int`):
      - 비밀번호를 변경할 **회원 ID**
    - **`request`** (`PasswordUpdateRequestDto`):
      - **새 비밀번호 요청 데이터**
    - **`user_service`** (`UserService`):
      - 회원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[UserResponseDto]`**
      - 수정된 **회원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 회원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    user = user_service.update_password(db, user_seq, password_update_request_dto.password)
    return CommonResponseDto(status="success", data=user, message="Password updated successfully")


@router.delete("/{user_seq}", response_model=CommonResponseDto[None], status_code=status.HTTP_200_OK)
@inject
def delete_user(
        user_seq: int,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """
    # 🗑 특정 회원 삭제 API

    ## 📝 Args:
    - **`user_seq`** (`int`):
      - 삭제할 **회원 ID**
    - **`user_service`** (`UserService`):
      - 회원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[None]`**
      - **삭제 성공 메시지 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 회원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    user_service.delete_user(db, user_seq)
    return CommonResponseDto(status="success", data=None, message="User deleted successfully")

@router.patch("/{user_seq}/soft-delete", response_model=CommonResponseDto[UserResponseDto], status_code=status.HTTP_200_OK)
@inject
def soft_delete_user(
        user_seq: int,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """
    # 🗄 특정 회원 소프트 삭제 API
    (실제 삭제 대신 `delete_at` 컬럼에 삭제 시점 기록)

    ## 📝 Args:
    - **`user_seq`** (`int`):
      - 소프트 삭제할 **회원 ID**
    - **`user_service`** (`UserService`):
      - 회원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[UserResponseDto]`**
      - 수정된 **회원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 회원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    user = user_service.soft_delete_user(db, user_seq)
    return CommonResponseDto(status="success", data=user, message="User soft deleted successfully")
