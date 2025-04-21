from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.jwt import decode_token
from app.core.database import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(*roles):
    def wrapper(user: User = Depends(get_current_user)):
        if str(user.role_id) not in map(str, roles):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return wrapper

def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user is an admin (assuming role_id 1 is admin)"""
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=403, 
            detail="The user doesn't have enough privileges"
        )
    return current_user
