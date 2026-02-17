from pydantic import BaseModel
from typing import List, Optional


class RoleCreate(BaseModel):
    name: str
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str]
    permissions: Optional[List[str]]


class RoleOut(BaseModel):
    id: str
    name: str
    permissions: List[str]
