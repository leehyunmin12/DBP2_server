import bcrypt


def hash_password(password: str) -> str:
    # 비밀번호를 받아서 비밀번호 + 무작위값 으로 해시 생성
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))