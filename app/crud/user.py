from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate , UserUpdate
from app.core.security import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    user = User(
        name=user_in.name,
        email=user_in.email,
        password=hash_password(user_in.password),
        role_id=user_in.role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password":
            setattr(user, field, hash_password(value))
        else:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user_role(db: Session, user_id: int, new_role_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.role_id = new_role_id
    db.commit()
    db.refresh(user)
    return user
