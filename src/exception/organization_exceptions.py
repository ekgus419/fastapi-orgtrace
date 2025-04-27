from fastapi import HTTPException, status

class OrganizationNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="조직을 찾을 수 없습니다.")

class OrganizationAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 조직입니다.")

class InvalidOrganizationLevelException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 조직 레벨입니다.")

class SubOrganizationsExistException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="하위 조직이 존재하여 삭제할 수 없습니다.")

class InvalidDivisionParentException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="부문(level=1)은 parent_seq 없이 생성해야 합니다.")

class MissingParentForHeadquarterException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="본부(level=2)는 반드시 parent_seq(부문 ID)가 필요합니다.")

class InvalidDivisionIdException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="유효한 부문 ID를 입력해야 합니다.")

class MissingParentForTeamException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="팀(level=3)은 반드시 parent_seq(본부 ID)가 필요합니다.")

class InvalidHeadquarterIdException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="유효한 본부 ID를 입력해야 합니다.")

class EmployeesExistInOrganizationException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 조직에 속한 직원이 존재하여 삭제할 수 없습니다.")

class OrganizationUpdateDataNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 데이터가 없습니다.")