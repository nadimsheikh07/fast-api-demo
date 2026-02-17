from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId

from app.models.role import RoleCreate, RoleUpdate, RoleOut
from app.db import roles_collection, users_collection
from app.auth.dependencies import require_roles

router = APIRouter()


# Create Role
@router.post("/", response_model=RoleOut)
async def create_role(role: RoleCreate, user=Depends(require_roles("admin"))):
    if await roles_collection.find_one({"name": role.name}):
        raise HTTPException(status_code=400, detail="Role already exists")
    role_dict = role.dict()
    result = await roles_collection.insert_one(role_dict)
    role_dict["id"] = str(result.inserted_id)
    return RoleOut(**role_dict)


# Get all Roles
@router.get("/", response_model=List[RoleOut])
async def get_roles(user=Depends(require_roles("admin"))):
    roles = await roles_collection.find().to_list(100)
    return [
        RoleOut(id=str(r["_id"]), name=r["name"], permissions=r["permissions"])
        for r in roles
    ]


# Update Role
@router.put("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: str, role_update: RoleUpdate, user=Depends(require_roles("admin"))
):
    update_data = {k: v for k, v in role_update.dict().items() if v is not None}
    await roles_collection.update_one({"_id": ObjectId(role_id)}, {"$set": update_data})
    updated_role = await roles_collection.find_one({"_id": ObjectId(role_id)})
    return RoleOut(
        id=str(updated_role["_id"]),
        name=updated_role["name"],
        permissions=updated_role["permissions"],
    )


# Delete Role
@router.delete("/{role_id}")
async def delete_role(role_id: str, user=Depends(require_roles("admin"))):
    await roles_collection.delete_one({"_id": ObjectId(role_id)})
    return {"detail": "Role deleted"}


# Assign Role to User
@router.post("/assign/{user_id}/{role_name}")
async def assign_role(
    user_id: str, role_name: str, user=Depends(require_roles("admin"))
):
    role = await roles_collection.find_one({"name": role_name})
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user_obj = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if role_name not in user_obj["roles"]:
        user_obj["roles"].append(role_name)
        await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"roles": user_obj["roles"]}}
        )
    return {"detail": f"Role '{role_name}' assigned to user '{user_obj['email']}'"}


# Remove Role from User
@router.post("/remove/{user_id}/{role_name}")
async def remove_role(
    user_id: str, role_name: str, user=Depends(require_roles("admin"))
):
    user_obj = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if role_name in user_obj["roles"]:
        user_obj["roles"].remove(role_name)
        await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"roles": user_obj["roles"]}}
        )
    return {"detail": f"Role '{role_name}' removed from user '{user_obj['email']}'"}
