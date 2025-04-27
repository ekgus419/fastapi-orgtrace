from fastapi import HTTPException, status

class RankNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="직위 정보를 찾을 수 없습니다.")

class RankAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 직위입니다.")

class RankUpdateDataNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 데이터가 없습니다.")