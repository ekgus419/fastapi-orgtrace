from fastapi import HTTPException, status

class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었습니다.")

class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 토큰입니다.")

class InvalidTokenSubjectMissingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰에 subject가 없습니다.")

class InvalidTokenScopeException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 토큰 범위입니다.")

class InvalidRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 리프레시 토큰입니다.")

class InvalidRefreshTokenSubjectMissingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰에 subject가 없습니다.")

class RefreshTokenLoggedOutException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 유효하지 않거나 로그아웃되었습니다.")

class RefreshTokenMismatchException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 일치하지않습니다.")
