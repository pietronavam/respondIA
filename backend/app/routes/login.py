from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..database import get_tenant_by_email
from ..auth import verify_password

router = APIRouter()


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(data: LoginForm):
    tenant = get_tenant_by_email(data.email)
    if not tenant or not tenant.hashed_password:
        raise HTTPException(401, "Correo o contraseña incorrectos")
    if not verify_password(data.password, tenant.hashed_password):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {
        "api_key": tenant.api_key,
        "business_name": tenant.name,
    }
