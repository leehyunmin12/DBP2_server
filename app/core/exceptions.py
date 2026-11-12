class AppError(Exception):
    
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


class EmailExistsError(AppError):
    def __init__(self):
        super().__init__(409, "EMAIL_EXISTS", "이미 가입된 이메일입니다.")


class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.")