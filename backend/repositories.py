from sqlalchemy import select, func, update
from .models import Case, Audit, utcnow

def scope(user):
    return [] if user.role == "admin" else [Case.owner_id == user.id]

def list_cases(db, user, status=None, search=None, offset=0, limit=50):
    filters = scope(user)
    if status:
        filters.append(Case.status == status)
    if search:
        filters.append(Case.title.icontains(search, autoescape=True))
    count = db.scalar(select(func.count()).select_from(Case).where(*filters))
    rows = db.scalars(select(Case).where(*filters).order_by(Case.id.desc()).offset(offset).limit(limit)).all()
    return count, rows

def metrics(db, user):
    rows = db.execute(select(Case.status, func.count()).where(*scope(user)).group_by(Case.status))
    counts = {"OPEN":0, "IN_PROGRESS":0, "RESOLVED":0}
    counts.update(dict(rows.all()))
    return {"total":sum(counts.values()), **counts}

def transition(db, case, status, version):
    result = db.execute(update(Case).where(Case.id == case.id, Case.version == version)
        .values(status=status, version=Case.version+1, updated_at=utcnow()))
    return result.rowcount == 1

def audit(db, case_id, actor_id, action, detail):
    db.add(Audit(case_id=case_id, actor_id=actor_id, action=action, detail=detail))
