from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, Audit, SessionToken
from .schemas import Login, NewUser, UserOut, NewCase, CaseOut, ChangeStatus, AuditOut, Status
from .security import verify_password, hash_password, issue_token, current_user, admin, bearer, token_hash, DUMMY_PASSWORD_HASH
from . import repositories as repo, services

router = APIRouter(prefix="/api")

@router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username))
    valid = verify_password(data.password, user.password_hash if user else DUMMY_PASSWORD_HASH)
    if not user or not valid:
        raise HTTPException(401, "Usuario o contraseña incorrectos")
    return {"access_token":issue_token(db,user), "token_type":"bearer", "user":UserOut.model_validate(user)}

@router.post("/logout", status_code=204)
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer),
           user: User = Depends(current_user), db: Session = Depends(get_db)):
    session = db.get(SessionToken, token_hash(credentials.credentials))
    if session:
        db.delete(session)
        db.commit()

@router.get("/users", response_model=list[UserOut])
def users(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.username)).all() if user.role == "admin" else [user]

@router.post("/users", response_model=UserOut, status_code=201)
def add_user(data: NewUser, user: User = Depends(admin), db: Session = Depends(get_db)):
    item = User(username=data.username, password_hash=hash_password(data.password), role=data.role)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El nombre de usuario ya existe")
    return item

@router.get("/cases")
def cases(status: Status | None = None, search: str | None = Query(None, max_length=160),
          offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
          user: User = Depends(current_user), db: Session = Depends(get_db)):
    count, rows = repo.list_cases(db,user,status,search,offset,limit)
    return {"total":count,"items":[CaseOut.model_validate(x) for x in rows]}

@router.post("/cases", response_model=CaseOut, status_code=201)
def create(data: NewCase, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return services.create_case(db,data,user)

@router.patch("/cases/{cid}", response_model=CaseOut)
def update(cid: int, data: ChangeStatus, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return services.change_status(db,cid,data,user)

@router.get("/cases/{cid}/audit", response_model=list[AuditOut])
def history(cid: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    services.accessible_case(db,cid,user)
    return db.scalars(select(Audit).where(Audit.case_id==cid).order_by(Audit.id)).all()

@router.get("/metrics")
def metrics(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return repo.metrics(db,user)
