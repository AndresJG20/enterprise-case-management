import os
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password

def main():
    password = os.environ.get("CASEFLOW_ADMIN_PASSWORD", "")
    if len(password) < 12:
        raise SystemExit("Set CASEFLOW_ADMIN_PASSWORD (minimum 12 characters)")
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username=="admin")):
            db.add(User(username="admin", password_hash=hash_password(password), role="admin"))
            db.commit()
            print("Administrator created")
        else:
            print("Administrator already exists; password unchanged")

if __name__ == "__main__":
    main()
