from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    roles: List[str] = ["user"]


class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    roles: Optional[List[str]]


class UserOut(BaseModel):
    id: str
    email: EmailStr
    roles: List[str]
