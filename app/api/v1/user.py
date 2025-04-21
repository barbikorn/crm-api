from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.crud import user as crud_user
from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(deps.get_db)) -> UserOut:
    if crud_user.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db, user_in)

@router.post("/login", response_model=Dict[str, str])
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    user = crud_user.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": str(user.role_id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(deps.get_current_user)) -> UserOut:
    return current_user

@router.put("/me", response_model=UserOut)
def update_me(user_update: UserUpdate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)) -> UserOut:
    updated = crud_user.update_user(db, current_user.id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.post("/register-admin", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_admin(
    user_in: UserCreate, 
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
) -> UserOut:
    if crud_user.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_in.role_id = 1
    return crud_user.create_user(db, user_in)

@router.put("/users/{user_id}/role/{role_id}", response_model=UserOut)
def update_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
) -> UserOut:
    updated_user = crud_user.update_user_role(db, user_id, role_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
) -> List[UserOut]:
    return db.query(User).all()
