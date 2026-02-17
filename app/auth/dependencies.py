from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.auth import decode_access_token
from app.db import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user = await users_collection.find_one({"email": payload["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def require_roles(*roles):
    async def role_checker(user=Depends(get_current_user)):
        if not any(role in user["roles"] for role in roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return role_checker
