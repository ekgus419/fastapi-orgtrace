from fastapi import Depends, Query, status
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.session import get_db
from src.dto.request.rank.rank_update_request_dto import RankUpdateRequestDto
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.dto.response.rank.rank_response_dto import RankResponseDto
from src.logging.api_logging_router import APILoggingRouter
from src.service.rank.rank_service import RankService
from src.dto.request.rank.rank_create_request_dto import RankCreateRequestDto
from src.dto.response.common_response_dto import CommonResponseDto

# 직위 관리 관련 API 엔드포인트를 정의하는 APIRouter
router = APILoggingRouter()


@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[RankResponseDto]])
@inject
def get_ranks(
        page: int = Query(1, ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'title')"),
        order: str = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        db: Session = Depends(get_db),
        rank_service: RankService = Depends(Provide[Container.rank_service])
):
    """
    # 📌 직위 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 직위 수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'name'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`rank_service`** (`RankService`): 직위 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[RankResponseDto]]`**
      직위 목록과 페이지네이션 정보 반환
    """
    ranks, total_count = rank_service.get_ranks(db, page, size, sort_by, order)
    rank_responses = [RankResponseDto.model_validate(e) for e in ranks]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=rank_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )


@router.get("/{rank_seq}", response_model=CommonResponseDto[RankResponseDto])
@inject
def get_rank(
        rank_seq: int,
        db: Session = Depends(get_db),
        rank_service: RankService = Depends(Provide[Container.rank_service])
):
    """
    # 🔍 특정 직위 조회 API

    ## 📝 Args:
    - **`rank_seq`** (`int`): 조회할 직위 **ID**
    - **`rank_service`** (`RankService`): 직위 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[RankResponseDto]`**
      조회된 **직위 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직위이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    rank = rank_service.get_rank_by_seq(db, rank_seq)
    return CommonResponseDto(status="success", data=rank, message=None)


@router.post("/", response_model=CommonResponseDto[RankResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_rank(
        rank_create_request_dto: RankCreateRequestDto,
        db: Session = Depends(get_db),
        rank_service: RankService = Depends(Provide[Container.rank_service])
):
    """
    # 🆕 새 직위 생성 API

    ## 📝 Args:
    - **`rank_create_request_dto`** (`RankCreateRequestDto`):
      - 직위 생성 요청 데이터
    - **`rank_service`** (`RankService`):
      - 직위 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[RankResponseDto]`**
      - 생성된 **직위 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 동일한 email이 이미 존재하는 경우 **`400 Bad Request`** 오류 반환
    """
    rank = rank_service.create_rank(db, rank_create_request=rank_create_request_dto)
    return CommonResponseDto(status="success", data=rank, message="Rank created successfully")


@router.patch("/{rank_seq}", response_model=CommonResponseDto[RankResponseDto], status_code=status.HTTP_200_OK)
@inject
def update_rank(
        rank_seq: int,
        rank_update_request_dto: RankUpdateRequestDto,
        db: Session = Depends(get_db),
        rank_service: RankService = Depends(Provide[Container.rank_service])
):
    """
    # 🔐 특정 직위 정보를 업데이트하는 API

    ## 📝 Args:
    - **`rank_seq`** (`int`):
      - 정보를 변경할 **직위 ID**
    - **`rank_update_request_dto`** (`RankUpdateRequestDto`):
      - **수정할 요청 데이터**
    - **`rank_service`** (`RankService`):
      - 직위 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[RankResponseDto]`**
      - 수정된 **직위 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직위가 존재하지 않을 경우 **`404 Not Found`** 오류 반환
      - 수정할 데이터가 없는 경우 **`400 Bad Request`** 오류 반환
    """
    rank = rank_service.update_rank(db, rank_seq, rank_update_request_dto)
    return CommonResponseDto(status="success", data=rank, message="Rank updated successfully")

@router.delete("/{rank_seq}", response_model=CommonResponseDto[None], status_code=status.HTTP_200_OK)
@inject
def delete_rank(
        rank_seq: int,
        db: Session = Depends(get_db),
        rank_service: RankService = Depends(Provide[Container.rank_service])
):
    """
    # 🗑 특정 직위 삭제 API

    ## 📝 Args:
    - **`rank_seq`** (`int`):
      - 삭제할 **직위 ID**
    - **`rank_service`** (`RankService`):
      - 직위 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[None]`**
      - **삭제 성공 메시지 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직위가 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    rank_service.delete_rank(db, rank_seq)
    return CommonResponseDto(status="success", data=None, message="Rank deleted successfully")


@router.patch("/{rank_seq}/soft-delete", response_model=CommonResponseDto[RankResponseDto], status_code=status.HTTP_200_OK)
@inject
def soft_delete_rank(
        rank_seq: int,
        db: Session = Depends(get_db),
        rank_service: RankService = Depends(Provide[Container.rank_service])
):
    """
    # 🗄 특정 직위 소프트 삭제 API
    (실제 삭제 대신 `delete_at` 컬럼에 삭제 시점 기록)

    ## 📝 Args:
    - **`rank_seq`** (`int`):
      - 소프트 삭제할 **직위 ID**
    - **`rank_service`** (`RankService`):
      - 직위 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[RankResponseDto]`**
      - 수정된 **직위 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직위가 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    rank = rank_service.soft_delete_rank(db, rank_seq)
    return CommonResponseDto(status="success", data=rank, message="Rank soft deleted successfully")
