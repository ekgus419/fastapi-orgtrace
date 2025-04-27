from fastapi import HTTPException, status

class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 자격 증명입니다.")

