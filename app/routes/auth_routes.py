from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserOut
from app.db import users_collection
from app.auth.security import hash_password, verify_password
from app.auth.auth import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict = user.dict()
    user_dict["password"] = hash_password(user.password)
    result = await users_collection.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return UserOut(**user_dict)


@router.post("/login")
async def login(form_data: UserCreate):
    user = await users_collection.find_one({"email": form_data.email})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "roles": user["roles"]})
    return {"access_token": token, "token_type": "bearer"}
