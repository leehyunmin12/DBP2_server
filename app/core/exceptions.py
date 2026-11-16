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

class UnauthorizedError(AppError):
    def __init__(self):
        super().__init__(401, "UNAUTHORIZED", "로그인이 필요합니다.")

class StockNotFoundError(AppError):
    def __init__(self):
        super().__init__(422, "STOCK_NOT_FOUND", "등록되지 않은 종목입니다.")

class TradeNotFoundError(AppError):
    def __init__(self) -> None:
        super().__init__(404, "TRADE_NOT_FOUND", "거래를 찾을 수 없습니다.")