from fastapi import Depends, Query, status
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.session import get_db
from src.dto.request.employee.employee_update_request_dto import EmployeeUpdateRequestDto
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.logging.api_logging_router import APILoggingRouter
from src.service.employee.employee_service import EmployeeService
from src.dto.request.employee.employee_create_request_dto import EmployeeCreateRequestDto
from src.dto.response.employee.employee_response_dto import EmployeeResponseDto
from src.dto.response.common_response_dto import CommonResponseDto

# 직원 관리 관련 API 엔드포인트를 정의하는 APIRouter
router = APILoggingRouter()


@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[EmployeeResponseDto]])
@inject
def get_employees(
        page: int = Query(1, ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'name')"),
        order: str = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        db: Session = Depends(get_db),
        employee_service: EmployeeService = Depends(Provide[Container.employee_service])
):
    """
    # 📌 직원 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 직원 수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'name'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`employee_service`** (`EmployeeService`): 직원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[EmployeeResponseDto]]`**
      직원 목록과 페이지네이션 정보 반환
    """
    employees, total_count = employee_service.get_employees(db, page, size, sort_by, order)
    employee_responses = [EmployeeResponseDto.model_validate(e) for e in employees]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=employee_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )


@router.get("/{employee_seq}", response_model=CommonResponseDto[EmployeeResponseDto])
@inject
def get_employee(
        employee_seq: int,
        db: Session = Depends(get_db),
        employee_service: EmployeeService = Depends(Provide[Container.employee_service])
):
    """
    # 🔍 특정 직원 조회 API

    ## 📝 Args:
    - **`employee_seq`** (`int`): 조회할 직원 **ID**
    - **`employee_service`** (`EmployeeService`): 직원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[EmployeeResponseDto]`**
      조회된 **직원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    employee = employee_service.get_employee_by_seq(db, employee_seq)
    return CommonResponseDto(status="success", data=employee, message=None)


@router.post("/", response_model=CommonResponseDto[EmployeeResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_employee(
        employee_create_request_dto: EmployeeCreateRequestDto,
        db: Session = Depends(get_db),
        employee_service: EmployeeService = Depends(Provide[Container.employee_service])
):
    """
    # 🆕 새 직원 생성 API

    ## 📝 Args:
    - **`employee_create_request_dto`** (`EmployeeCreateRequestDto`):
      - 직원 생성 요청 데이터
    - **`employee_service`** (`EmployeeService`):
      - 직원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[EmployeeResponseDto]`**
      - 생성된 **직원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 동일한 email이 이미 존재하는 경우 **`400 Bad Request`** 오류 반환
    """
    employee = employee_service.create_employee(db, employee_create_request_dto)
    return CommonResponseDto(status="success", data=employee, message="Employee created successfully")


@router.patch("/{employee_seq}", response_model=CommonResponseDto[EmployeeResponseDto], status_code=status.HTTP_200_OK)
@inject
def update_employee(
        employee_seq: int,
        employee_update_request_dto: EmployeeUpdateRequestDto,
        db: Session = Depends(get_db),
        employee_service: EmployeeService = Depends(Provide[Container.employee_service])
):
    """
    # 🔐 특정 직원 정보를 업데이트하는 API

    ## 📝 Args:
    - **`employee_seq`** (`int`):
      - 정보를 변경할 **직원 ID**
    - **`employee_update_request_dto`** (`EmployeeUpdateRequestDto`):
      - **수정할 요청 데이터**
    - **`employee_service`** (`EmployeeService`):
      - 직원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[EmployeeResponseDto]`**
      - 수정된 **직원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
      - 수정할 데이터가 없는 경우 **`400 Bad Request`** 오류 반환
    """
    employee = employee_service.update_employee(db, employee_seq, employee_update_request_dto)
    return CommonResponseDto(status="success", data=employee, message="Employee updated successfully")

@router.delete("/{employee_seq}", response_model=CommonResponseDto[None], status_code=status.HTTP_200_OK)
@inject
def delete_employee(
        employee_seq: int,
        db: Session = Depends(get_db),
        employee_service: EmployeeService = Depends(Provide[Container.employee_service])
):
    """
    # 🗑 특정 직원 삭제 API

    ## 📝 Args:
    - **`employee_seq`** (`int`):
      - 삭제할 **직원 ID**
    - **`employee_service`** (`EmployeeService`):
      - 직원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[None]`**
      - **삭제 성공 메시지 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    employee_service.delete_employee(db, employee_seq)
    return CommonResponseDto(status="success", data=None, message="Employee deleted successfully")


@router.patch("/{employee_seq}/soft-delete", response_model=CommonResponseDto[EmployeeResponseDto], status_code=status.HTTP_200_OK)
@inject
def soft_delete_employee(
        employee_seq: int,
        db: Session = Depends(get_db),
        employee_service: EmployeeService = Depends(Provide[Container.employee_service])
):
    """
    # 🗄 특정 직원 소프트 삭제 API
    (실제 삭제 대신 `delete_at` 컬럼에 삭제 시점 기록)

    ## 📝 Args:
    - **`employee_seq`** (`int`):
      - 소프트 삭제할 **직원 ID**
    - **`employee_service`** (`EmployeeService`):
      - 직원 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[EmployeeResponseDto]`**
      - 수정된 **직원 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 직원이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    employee = employee_service.soft_delete_employee(db, employee_seq)
    return CommonResponseDto(status="success", data=employee, message="Employee soft deleted successfully")
