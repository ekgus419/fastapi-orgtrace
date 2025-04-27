from fastapi import HTTPException, status

class OrganizationHistoryNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="조직 히스토리가 없습니다.")
