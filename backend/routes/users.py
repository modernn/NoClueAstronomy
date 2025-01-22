from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

class User(BaseModel):
    username: str
    email: EmailStr
    password: str

users = []

@router.post("/users")
def create_user(user: User):
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    users.append(user.dict())
    return {"message": "User created successfully", "user": user}
