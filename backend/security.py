import hashlib
import hmac
import secrets
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, SessionToken, utcnow
from .config import SESSION_HOURS

bearer = HTTPBearer(auto_error=False)

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600000)
    return salt + ":" + digest.hex()

def verify_password(password, encoded):
    salt, expected = encoded.split(":")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600000)
    return hmac.compare_digest(digest.hex(), expected)

def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()

def issue_token(db, user):
    raw = secrets.token_urlsafe(32)
    db.add(SessionToken(token_hash=token_hash(raw), user_id=user.id,
                        expires=utcnow() + timedelta(hours=SESSION_HOURS)))
    db.commit()
    return raw

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
                 db: Session = Depends(get_db)):
    session = db.get(SessionToken, token_hash(credentials.credentials)) if credentials else None
    if not session or session.expires <= utcnow():
        raise HTTPException(401, "La sesión no es válida o ha caducado", headers={"WWW-Authenticate":"Bearer"})
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, "Usuario no encontrado")
    return user

def admin(user: User = Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Se requieren permisos de administrador")
    return user
