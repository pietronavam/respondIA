from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from ..database import get_tenant_by_email

router = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(data: LoginForm):
    tenant = get_tenant_by_email(data.email)
    if not tenant or not tenant.hashed_password:
        raise HTTPException(401, "Correo o contraseña incorrectos")
    if not pwd_ctx.verify(data.password, tenant.hashed_password):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {
        "api_key": tenant.api_key,
        "business_name": tenant.name,
    }
