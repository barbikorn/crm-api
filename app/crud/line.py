from sqlalchemy.orm import Session
from app.models.line import LineMessage, LineUser
from app.schemas.line import LineMessageCreate, LineUserCreate

def create_line_message(db: Session, message_in: LineMessageCreate):
    message = LineMessage(**message_in.dict())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def create_line_user(db: Session, user_in: LineUserCreate):
    user = LineUser(**user_in.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_line_message(db: Session, message_id: int):
    return db.query(LineMessage).filter(LineMessage.id == message_id).first()

def get_line_user(db: Session, user_id: str):
    return db.query(LineUser).filter(LineUser.user_id == user_id).first()

def update_line_message(db: Session, message_id: int, message_in: LineMessageCreate):
    message = db.query(LineMessage).filter(LineMessage.id == message_id).first()
    if message:
        for key, value in message_in.dict(exclude_unset=True).items():
            setattr(message, key, value)
        db.commit()
        db.refresh(message)
    return message

def delete_line_message(db: Session, message_id: int):
    message = db.query(LineMessage).filter(LineMessage.id == message_id).first()
    if message:
        db.delete(message)
        db.commit()
    return message

def update_line_user(db: Session, user_id: str, user_in: LineUserCreate):
    user = db.query(LineUser).filter(LineUser.user_id == user_id).first()
    if user:
        for key, value in user_in.dict(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_line_user(db: Session, user_id: str):
    user = db.query(LineUser).filter(LineUser.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def get_all_line_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LineMessage).offset(skip).limit(limit).all()

def get_all_line_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LineUser).offset(skip).limit(limit).all()