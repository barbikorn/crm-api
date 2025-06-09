from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role_id: int = 2  # Default to regular user role

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role_id: int | None = None  # Added role_id field

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role_id: int

    class Config:
        from_attributes = True
