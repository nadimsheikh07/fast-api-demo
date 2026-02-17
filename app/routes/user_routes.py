from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserUpdate, UserOut
from app.db import users_collection
from bson import ObjectId
from app.auth.dependencies import require_roles
from app.auth.security import hash_password
from typing import List

router = APIRouter()


@router.get("/", response_model=List[UserOut])
async def get_users(user=Depends(require_roles("admin"))):
    users = await users_collection.find().to_list(100)
    return [
        UserOut(id=str(u["_id"]), email=u["email"], roles=u["roles"]) for u in users
    ]


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str, user_update: UserUpdate, user=Depends(require_roles("admin"))
):
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    await users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return UserOut(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        roles=updated_user["roles"],
    )


@router.delete("/{user_id}")
async def delete_user(user_id: str, user=Depends(require_roles("admin"))):
    await users_collection.delete_one({"_id": ObjectId(user_id)})
    return {"detail": "User deleted"}
