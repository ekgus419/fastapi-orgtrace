from fastapi import Depends, Query
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.session import get_db
from src.logging.api_logging_router import APILoggingRouter
from src.service.organization.organization_history_service import OrganizationHistoryService
from src.dto.response.common_response_dto import CommonResponseDto
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.dto.response.organization.organization_history_response_dto import OrganizationHistoryResponseDto

# 조직 히스토리 관련 API 엔드포인트를 정의하는 APIRouter
router = APILoggingRouter()


@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[OrganizationHistoryResponseDto]])
@inject
def get_organization_histories(
        page: int = Query(1, ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'name')"),
        order: str = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        db: Session = Depends(get_db),
        organization_history_service: OrganizationHistoryService = Depends(Provide[Container.organization_history_service])
):
    """
    # 📌 조직 히스토리 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 조직 히스토리수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'name'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`organization_history_service`** (`OrganizationHistoryService`): 조직 히스토리 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[OrganizationHistoryResponseDto]]`**
      조직 히스토리 목록과 페이지네이션 정보 반환
    """
    histories, total_count = organization_history_service.get_organization_histories(db, page, size, sort_by, order)
    organization_history_responses = [OrganizationHistoryResponseDto.model_validate(h) for h in histories]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=organization_history_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )

@router.get("/{organization_history_seq}", response_model=CommonResponseDto[OrganizationHistoryResponseDto])
@inject
def get_organization_history(
        organization_history_seq: int,
        db: Session = Depends(get_db),
        organization_history_service: OrganizationHistoryService = Depends(Provide[Container.organization_history_service])
):
    """
    # 🔍 특정 조직 히스토리 조회 API

    ## 📝 Args:
    - **`organization_history_seq`** (`int`): 조회할 조직 히스토리 **ID**
    - **`organization_history_service`** (`OrganizationHistoryService`): 조직 히스토리 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationHistoryResponseDto]`**
      조회된 **조직 히스토리 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 조직 히스토리가 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    organization_history = organization_history_service.get_organization_history_by_seq(db, organization_history_seq)
    return CommonResponseDto(status="success", data=organization_history, message=None)
