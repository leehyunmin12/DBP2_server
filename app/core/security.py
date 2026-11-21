import bcrypt


def hash_password(password: str) -> str:
    # 비밀번호를 받아서 비밀번호 + 무작위값 으로 해시 생성
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    # 72바이트를 넘는 비밀번호는 가입할 수 없으므로 항상 불일치로 처리한다. (bcrypt가 에러를 내는 것을 막는다)
    if len(password.encode("utf-8")) > 72:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))