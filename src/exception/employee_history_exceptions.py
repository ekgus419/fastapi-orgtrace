from fastapi import HTTPException, status

class EmployeeHistoryNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="직원 히스토리가 없습니다.")
