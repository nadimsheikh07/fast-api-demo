from fastapi import FastAPI
from app.routes import user_routes, auth_routes, role_routes

app = FastAPI(title="FastAPI Mongo Role/Permission")

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(role_routes.router, prefix="/roles", tags=["Roles"])
