import os
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password

def main():
    password = os.environ.get("CASEFLOW_ADMIN_PASSWORD", "")
    if len(password) < 12:
        raise SystemExit("Define CASEFLOW_ADMIN_PASSWORD con al menos 12 caracteres")
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username=="admin")):
            db.add(User(username="admin", password_hash=hash_password(password), role="admin"))
            db.commit()
            print("Usuario administrador creado")
        else:
            print("El administrador ya existe; se mantiene su contraseña")

if __name__ == "__main__":
    main()
