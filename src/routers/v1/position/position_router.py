from fastapi import Depends, Query, status
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.session import get_db
from src.dto.request.position.position_update_request_dto import PositionUpdateRequestDto
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.dto.response.position.position_response_dto import PositionResponseDto
from src.logging.api_logging_router import APILoggingRouter
from src.service.position.position_service import PositionService
from src.dto.request.position.position_create_request_dto import PositionCreateRequestDto
from src.dto.response.common_response_dto import CommonResponseDto

# 직책 관리 관련 API 엔드포인트를 정의하는 APIRouter
router = APILoggingRouter()


@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[PositionResponseDto]])
@inject
def get_positions(
        page: int = Query(1, ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'title')"),
        order: str = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        db: Session = Depends(get_db),
        position_service: PositionService = Depends(Provide[Container.position_service])
):
    """
    # 📌 직책 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 직책 수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'name'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`position_service`** (`PositionService`): 직책 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[PositionResponseDto]]`**
      직책 목록과 페이지네이션 정보 반환
    """
    positions, total_count = position_service.get_positions(db, page, size, sort_by, order)
    position_responses = [PositionResponseDto.model_validate(e) for e in positions]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=position_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )


@router.get("/{position_seq}", response_model=CommonResponseDto[PositionResponseDto])
@inject
def get_position(
        position_seq: int,
        db: Session = Depends(get_db),
        position_service: PositionService = Depends(Provide[Container.position_service])
):
    """
    # 🔍 특정 직책 조회 API

    ## 📝 Args:
    - **`position_seq`** (`int`): 조회할 직책 **ID**
    - **`position_service`** (`PositionService`): 직책 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PositionResponseDto]`**
      조회된 **직책 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직책이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    position = position_service.get_position_by_seq(db, position_seq)
    return CommonResponseDto(status="success", data=position, message=None)


@router.post("/", response_model=CommonResponseDto[PositionResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_position(
        position_create_request_dto: PositionCreateRequestDto,
        db: Session = Depends(get_db),
        position_service: PositionService = Depends(Provide[Container.position_service])
):
    """
    # 🆕 새 직책 생성 API

    ## 📝 Args:
    - **`position_create_request_dto`** (`PositionCreateRequestDto`):
      - 직책 생성 요청 데이터
    - **`position_service`** (`PositionService`):
      - 직책 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PositionResponseDto]`**
      - 생성된 **직책 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 동일한 title 이미 존재하는 경우 **`400 Bad Request`** 오류 반환
    """
    position = position_service.create_position(db, position_create_request=position_create_request_dto)
    return CommonResponseDto(status="success", data=position, message="Position created successfully")


@router.patch("/{position_seq}", response_model=CommonResponseDto[PositionResponseDto], status_code=status.HTTP_200_OK)
@inject
def update_position(
        position_seq: int,
        position_update_request_dto: PositionUpdateRequestDto,
        db: Session = Depends(get_db),
        position_service: PositionService = Depends(Provide[Container.position_service])
):
    """
    # 🔐 특정 직책 정보를 업데이트하는 API

    ## 📝 Args:
    - **`position_seq`** (`int`):
      - 정보를 변경할 **직책 ID**
    - **`position_update_request_dto`** (`PositionUpdateRequestDto`):
      - **수정할 요청 데이터**
    - **`position_service`** (`PositionService`):
      - 직책 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PositionResponseDto]`**
      - 수정된 **직책 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직책이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
      - 수정할 데이터가 없는 경우 **`400 Bad Request`** 오류 반환
    """
    position = position_service.update_position(db, position_seq, position_update_request_dto)
    return CommonResponseDto(status="success", data=position, message="Position updated successfully")

@router.delete("/{position_seq}", response_model=CommonResponseDto[None], status_code=status.HTTP_200_OK)
@inject
def delete_position(
        position_seq: int,
        db: Session = Depends(get_db),
        position_service: PositionService = Depends(Provide[Container.position_service])
):
    """
    # 🗑 특정 직책 삭제 API

    ## 📝 Args:
    - **`position_seq`** (`int`):
      - 삭제할 **직책 ID**
    - **`position_service`** (`PositionService`):
      - 직책 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[None]`**
      - **삭제 성공 메시지 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직책이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    position_service.delete_position(db, position_seq)
    return CommonResponseDto(status="success", data=None, message="Position deleted successfully")


@router.patch("/{position_seq}/soft-delete", response_model=CommonResponseDto[PositionResponseDto], status_code=status.HTTP_200_OK)
@inject
def soft_delete_position(
        position_seq: int,
        db: Session = Depends(get_db),
        position_service: PositionService = Depends(Provide[Container.position_service])
):
    """
    # 🗄 특정 직책 소프트 삭제 API
    (실제 삭제 대신 `delete_at` 컬럼에 삭제 시점 기록)

    ## 📝 Args:
    - **`position_seq`** (`int`):
      - 소프트 삭제할 **직책 ID**
    - **`position_service`** (`PositionService`):
      - 직책 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PositionResponseDto]`**
      - 수정된 **직책 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직책이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    position = position_service.soft_delete_position(db, position_seq)
    return CommonResponseDto(status="success", data=position, message="Position soft deleted successfully")
