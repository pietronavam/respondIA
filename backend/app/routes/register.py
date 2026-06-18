from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database import create_tenant, save_setting

router = APIRouter()


class RegisterForm(BaseModel):
    name: str
    email: str = ""


@router.post("/register")
def register(data: RegisterForm):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "El nombre del negocio es requerido")

    # Sandbox number shared — each tenant gets isolated by api_key
    tenant = create_tenant(name=name, phone_number=f"whatsapp:+14155238886")
    save_setting(tenant.id, "business_name", name)

    return {
        "api_key": tenant.api_key,
        "name": tenant.name,
        "panel_url": "https://respond-ia.streamlit.app/",
    }
