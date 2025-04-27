from fastapi import Depends, Query
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.session import get_db
from src.logging.api_logging_router import APILoggingRouter
from src.service.employee.employee_history_service import EmployeeHistoryService
from src.dto.response.common_response_dto import CommonResponseDto
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.dto.response.employee.employee_history_response_dto import EmployeeHistoryResponseDto

# 직원 히스토리 관련 API 엔드포인트를 정의하는 APIRouter
router = APILoggingRouter()

@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[EmployeeHistoryResponseDto]])
@inject
def get_employee_histories(
        page: int = Query(1, ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'name')"),
        order: str = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        db: Session = Depends(get_db),
        employee_history_service: EmployeeHistoryService = Depends(Provide[Container.employee_history_service])
):
    """
    # 📌 직원 히스토리 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 직원 히스토리수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'name'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`employee_history_service`** (`EmployeeHistoryService`): 직원 히스토리 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[EmployeeHistoryResponseDto]]`**
      직원 히스토리 목록과 페이지네이션 정보 반환
    """
    histories, total_count = employee_history_service.get_employee_histories(db, page, size, sort_by, order)
    employee_history_responses = [EmployeeHistoryResponseDto.model_validate(h) for h in histories]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=employee_history_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )

@router.get("/{employee_history_seq}", response_model=CommonResponseDto[EmployeeHistoryResponseDto])
@inject
def get_employee_history(
        employee_history_seq: int,
        db: Session = Depends(get_db),
        employee_history_service: EmployeeHistoryService = Depends(Provide[Container.employee_history_service])
):
    """
    # 🔍 특정 직원 히스토리 조회 API

    ## 📝 Args:
    - **`employee_history_seq`** (`int`): 조회할 직원 히스토리 **ID**
    - **`employee_history_service`** (`EmployeeHistoryService`): 직원 히스토리 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[EmployeeHistoryResponseDto]`**
      조회된 **직원 히스토리 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직원 히스토리가 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    employee_history = employee_history_service.get_employee_history_by_seq(db, employee_history_seq)
    return CommonResponseDto(status="success", data=employee_history, message=None)
