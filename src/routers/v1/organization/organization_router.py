from fastapi import Depends, status, Query
from dependency_injector.wiring import inject, Provide
from sqlalchemy.orm import Session
from typing import List, Optional
from src.core.container import Container
from src.core.session import get_db
from src.dto.request.organization.organization_create_request_dto import TeamCreateRequestDto, HeadquartersCreateRequestDto, DepartmentCreateRequestDto
from src.dto.request.organization.organization_update_request_dto import OrganizationNameAndVisibleUpdateRequestDto, OrganizationMoveRequestDto
from src.dto.response.organization.organization_response_dto import OrganizationResponseDto
from src.dto.response.common_response_dto import CommonResponseDto
from src.dto.response.paginated_response_dto import PaginatedResponseDto
from src.logging.api_logging_router import APILoggingRouter
from src.service.organization.organization_service import OrganizationService

router = APILoggingRouter()

@router.get("/", response_model=CommonResponseDto[PaginatedResponseDto[OrganizationResponseDto]])
@inject
def get_organizations(
        page: int = Query(1,  ge=1, description="현재 페이지 (1부터 시작)"),
        size: int = Query(10, ge=1, description="페이지 크기"),
        sort_by: str | None       = Query(None, description="정렬 기준 컬럼명 (예: 'seq', 'name')"),
        order: str                = Query("asc", regex="^(asc|desc)$", description="정렬 순서 ('asc' 또는 'desc')"),
        level: Optional[int]      = Query(None, description="조직 수준 (1: 부문, 2: 본부, 3: 팀)"),
        parent_seq: Optional[int] = Query(None, description="상위 조직 seq"),
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 📌 조직 목록 조회 API (페이징 및 정렬 지원)

    ## 📝 Args:
    - **`page`** (`int`): 현재 페이지 번호 (**1부터 시작**)
    - **`size`** (`int`): 페이지 크기 (**한 페이지당 조직 수**)
    - **`sort_by`** (`str | None`): 정렬 기준 컬럼명
      - 예시: `'seq'`, `'name'`
    - **`order`** (`str`): 정렬 방향
      - `"asc"` (오름차순) | `"desc"` (내림차순)
    - **`level`** (`int`): 조직 수준
      - `"1"` (부문) | `"2"` (본부) | `"3"` (팀)
    - **`parent_seq`** (`int`): 상위 조직 seq
    - **`organization_service`** (`OrganizationService`): 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[PaginatedResponseDto[OrganizationResponseDto]]`**
      조직 목록과 페이지네이션 정보 반환
    """
    organizations, total_count = organization_service.get_organizations(db, page, size, sort_by, order, level, parent_seq)
    organization_responses = [OrganizationResponseDto.model_validate(e) for e in organizations]
    total_pages = (total_count + size - 1) // size

    return CommonResponseDto(
        status="success",
        data=PaginatedResponseDto(
            items=organization_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages
        ),
        message=None
    )


@router.get("/hierarchy", response_model=CommonResponseDto[List[OrganizationResponseDto]])
@inject
def get_organization_hierarchy(
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    - 부문 → 본부 → 팀 순서로 계층 구조를 반환
    # 📌 전체 조직도 조회 API (트리 구조)

    ## 📝 Args:
    - **`organization_service`** (`OrganizationService`): 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[List[OrganizationResponseDto]]`**
      전체 조직도 목록 반환 (부문 → 본부 → 팀 순서로 계층 구조를 반환)
    """
    organization_tree = organization_service.get_organization_tree(db)
    return CommonResponseDto(status="success", data=organization_tree, message=None)


@router.get("/{organization_seq}", response_model=CommonResponseDto[OrganizationResponseDto])
@inject
def get_organization(
        organization_seq: int,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🆕 특정 조직 조회 API

    ## 📝 Args:
    - **`organization_seq`** (`int`): 조회할 조직 ID
    - **`organization_service`**: 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - `CommonResponseDto[OrganizationResponseDto]`: 조회된 조직 정보

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 조직이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    organization = organization_service.get_organization_by_seq(db, organization_seq)
    return CommonResponseDto(status="success", data=organization, message=None)

@router.post("/departments", response_model=CommonResponseDto[OrganizationResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_department(
        department_create_request_dto: DepartmentCreateRequestDto,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🆕 부문 생성 API (level=1)

    ## 📝 Args:
    - **`department_create_request_dto`** (`DepartmentCreateRequestDto`):
      - 부문 생성 요청 데이터
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationResponseDto]`**
      - 생성된 **부문 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 잘못된 조직 레벨인 경우 **`400 Bad Request`** 오류 반환
      - parent_seq 가 이미 존재하는 경우 **`400 Bad Request`** 오류 반환
    """
    department = organization_service.create_department(db, department_create_request_dto)
    return CommonResponseDto(status="success", data=department, message="Department created successfully")


@router.post("/headquarters", response_model=CommonResponseDto[OrganizationResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_headquarters(
        headquarters_create_request_dto: HeadquartersCreateRequestDto,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🆕 본부 생성 API (level=2)

    ## 📝 Args:
    - **`headquarters_create_request_dto`** (`HeadquartersCreateRequestDto`):
      - 본부 생성 요청 데이터
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationResponseDto]`**
      - 생성된 **본부 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 잘못된 조직 레벨인 경우 **`400 Bad Request`** 오류 반환
      - parent_seq 가 존재하지 않는 경우 **`400 Bad Request`** 오류 반환
      - 유효한 부문 ID가 아닌 경우 **`400 Bad Request`** 오류 반환
    """
    headquarters = organization_service.create_headquarters(db, headquarters_create_request_dto)
    return CommonResponseDto(status="success", data=headquarters, message="Headquarters created successfully")


@router.post("/teams", response_model=CommonResponseDto[OrganizationResponseDto], status_code=status.HTTP_201_CREATED)
@inject
def create_team(
        team_create_request_dto: TeamCreateRequestDto,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🆕 팀 생성 API (level=3)

    ## 📝 Args:
    - **`team_create_request_dto`** (`TeamCreateRequestDto`):
      - 팀 생성 요청 데이터
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationResponseDto]`**
      - 생성된 **팀 정보 반환**

     ## ⚠️ Raises:
    - **`HTTPException`**:
      - 잘못된 조직 레벨인 경우 **`400 Bad Request`** 오류 반환
      - parent_seq 가 존재하지 않는 경우 **`400 Bad Request`** 오류 반환
      - 유효한 본부 ID가 아닌 경우 **`400 Bad Request`** 오류 반환
    """
    team = organization_service.create_team(db, team_create_request_dto)
    return CommonResponseDto(status="success", data=team, message="Team created successfully")


@router.patch("/{organization_seq}", response_model=CommonResponseDto[OrganizationResponseDto])
@inject
def update_organization(
        organization_seq: int,
        request: OrganizationNameAndVisibleUpdateRequestDto,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🔐 특정 조직의 이름과 노출 여부를 업데이트 하는 API
    - `name`, `is_visible` 변경 가능

    ## 📝 Args:
    - **`organization_seq`** (`int`):
      - 정보를 변경할 **조직 ID**
    - **`request`** (`OrganizationUpdateRequestDto`):
      - **수정할 요청 데이터**
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationResponseDto]`**
      - 수정된 **조직 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 조직이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
      - 수정할 데이터가 없는 경우 **`400 Bad Request`** 오류 반환
    """
    organization = organization_service.update_organization(db, organization_seq, request)
    return CommonResponseDto(status="success", data=organization, message="Organization updated successfully")

@router.patch("/{organization_seq}/move", response_model=CommonResponseDto[OrganizationResponseDto])
@inject
def move_organization(
        organization_move_request: OrganizationMoveRequestDto,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🔐 특정 조직이 속한 조직 정보를 업데이트 하는 API
    - `parent_seq`를 변경하여 조직을 이동
    - `level` 변경은 불가능

    ## 📝 Args:
    - **`organization_move_request`** (`OrganizationMoveRequestDto`):
      - 이동할 조직과 새 부모 조직 정보를 담은 DTO
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationResponseDto]`**
      - 수정된 **조직 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 조직이 존재하지 않을 경우 **`404 Not Found`** 오류 반환
    """
    organization = organization_service.move_organization(db, organization_move_request)
    return CommonResponseDto(status="success", data=organization, message="Organization moved successfully")

@router.delete("/{organization_seq}", response_model=CommonResponseDto[None])
@inject
def delete_organization(
        organization_seq: int,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🗄 특정 조직 삭제 API
    - 하위 조직이 있을 경우 삭제 불가 (물리 삭제)

    ## 📝 Args:
    - **`organization_seq`** (`int`):
      - 삭제할 **조직 ID**
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[None]`**
      - **삭제 성공 메시지 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 조직에 속한 직원이 존재하는 경우 **`400 Bad request`** 오류 반환
      - 하위 조직이 존재하는 경우 경우 **`400 Bad request`** 오류 반환
      - 해당 조직이 존재하지 않는 경우 **`404 Not Found`** 오류 반환
    """
    organization_service.delete_organization(db, organization_seq)
    return CommonResponseDto(status="success", data=None, message="Organization deleted successfully")

@router.patch("/{organization_seq}/soft-delete", response_model=CommonResponseDto[OrganizationResponseDto], status_code=status.HTTP_200_OK)
@inject
def soft_delete_organization(
        organization_seq: int,
        db: Session = Depends(get_db),
        organization_service: OrganizationService = Depends(Provide[Container.organization_service])
):
    """
    # 🗄 특정 조직 소프트 삭제 API
    (실제 삭제 대신 `deleted_at` 컬럼에 삭제 시점 기록)

    ## 📝 Args:
    - **`organization_seq`** (`int`):
      - 소프트 삭제할 **조직 ID**
    - **`organization_service`** (`OrganizationService`):
      - 조직 서비스 **의존성 주입**

    ## 📤 Returns:
    - **`CommonResponseDto[OrganizationResponseDto]`**
      - 수정된 **조직 정보 반환**

    ## ⚠️ Raises:
    - **`HTTPException`**:
      - 조직에 속한 직원이 존재하는 경우 **`400 Bad request`** 오류 반환
      - 하위 조직이 존재하는 경우 경우 **`400 Bad request`** 오류 반환
      - 해당 조직이 존재하지 않는 경우 **`404 Not Found`** 오류 반환
    """
    organization = organization_service.soft_delete_organization(db, organization_seq)
    return CommonResponseDto(status="success", data=organization, message="Organization soft deleted successfully")
