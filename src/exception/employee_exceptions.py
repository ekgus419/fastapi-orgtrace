from fastapi import HTTPException, status

class EmployeeNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="직원 정보를 찾을 수 없습니다.")

class EmployeeAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 직원입니다.")

class EmployeeUpdateDataNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 데이터가 없습니다.")