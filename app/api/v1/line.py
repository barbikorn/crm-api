from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.line import LineMessageCreate, LineMessageOut, LineUserCreate, LineUserOut
from app.crud import line as crud_line
from app.api import deps

router = APIRouter()

@router.post("/line/messages", response_model=LineMessageOut)
def create_line_message(
    message: LineMessageCreate, 
    db: Session = Depends(deps.get_db)
):
    return crud_line.create_line_message(db, message)

@router.post("/line/users", response_model=LineUserOut)
def create_line_user(
    user: LineUserCreate, 
    db: Session = Depends(deps.get_db)
):
    return crud_line.create_line_user(db, user)

@router.get("/line/messages/{message_id}", response_model=LineMessageOut)
def get_line_message(
    message_id: int, 
    db: Session = Depends(deps.get_db)
):
    message = crud_line.get_line_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/line/users/{user_id}", response_model=LineUserOut)
def get_line_user(
    user_id: str, 
    db: Session = Depends(deps.get_db)
):
    user = crud_line.get_line_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/line/messages/{message_id}", response_model=LineMessageOut)
def update_line_message(
    message_id: int, 
    message: LineMessageCreate, 
    db: Session = Depends(deps.get_db)
):
    updated_message = crud_line.update_line_message(db, message_id, message)
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return updated_message

@router.delete("/line/messages/{message_id}", response_model=LineMessageOut)
def delete_line_message(
    message_id: int, 
    db: Session = Depends(deps.get_db)
):
    message = crud_line.delete_line_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.put("/line/users/{user_id}", response_model=LineUserOut)
def update_line_user(
    user_id: str, 
    user: LineUserCreate, 
    db: Session = Depends(deps.get_db)
):
    updated_user = crud_line.update_line_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/line/users/{user_id}", response_model=LineUserOut)
def delete_line_user(
    user_id: str, 
    db: Session = Depends(deps.get_db)
):
    user = crud_line.delete_line_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/line/messages", response_model=List[LineMessageOut])
def get_all_line_messages(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db)
):
    return crud_line.get_all_line_messages(db, skip=skip, limit=limit)

@router.get("/line/users", response_model=List[LineUserOut])
def get_all_line_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db)
):
    return crud_line.get_all_line_users(db, skip=skip, limit=limit)