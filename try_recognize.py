import sys
from pathlib import Path

from app.core.database import SessionLocal       # database.py에서 세션을 만드는 이름
from app.services.capture import recognize

with SessionLocal() as db:
    for c in recognize(db, Path(sys.argv[1]).read_bytes(), "image/png"):
        print(c)