from fastapi import HTTPException
from .models import Case, User
from . import repositories as repo

TRANSITIONS = {"OPEN":{"IN_PROGRESS"}, "IN_PROGRESS":{"OPEN","RESOLVED"}, "RESOLVED":{"IN_PROGRESS"}}

def accessible_case(db, cid, user):
    case = db.get(Case, cid)
    if not case or (user.role != "admin" and case.owner_id != user.id):
        raise HTTPException(404, "Case not found")
    return case

def create_case(db, data, user):
    if user.role != "admin" and data.owner_id != user.id:
        raise HTTPException(403, "Cannot assign another user")
    if not db.get(User, data.owner_id):
        raise HTTPException(422, "Unknown owner")
    case = Case(**data.model_dump(), status="OPEN")
    db.add(case)
    db.flush()
    repo.audit(db, case.id, user.id, "CREATED", "Case registered")
    db.commit()
    return case

def change_status(db, cid, data, user):
    case = accessible_case(db, cid, user)
    old = case.status
    if case.version != data.version:
        raise HTTPException(409, "Case changed; refresh")
    if data.status not in TRANSITIONS[old]:
        raise HTTPException(422, "Invalid state transition")
    if not repo.transition(db, case, data.status, data.version):
        db.rollback()
        raise HTTPException(409, "Case changed; refresh")
    repo.audit(db, case.id, user.id, "STATUS_CHANGED", f"{old} -> {data.status}")
    db.commit()
    db.refresh(case)
    return case
