from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from ..auth import require_tenant
from ..database import Tenant, save_setting, get_setting
from ..services.ocr import extract_text_from_pdf, extract_text_from_image

router = APIRouter(prefix="/catalog")

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}


@router.post("/upload")
async def upload_catalog(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(require_tenant),
):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Tipo de archivo no soportado: {content_type}")

    data = await file.read()
    file_type = ALLOWED_TYPES[content_type]

    if file_type == "pdf":
        text = extract_text_from_pdf(data)
    else:
        text = extract_text_from_image(data, suffix=f".{file_type}")

    if not text:
        raise HTTPException(422, "No se pudo extraer texto del archivo")

    save_setting(tenant.id, "catalog", text)
    return {"status": "ok", "characters": len(text), "preview": text[:500]}


@router.get("/")
def get_current_catalog(tenant: Tenant = Depends(require_tenant)):
    return {"catalog": get_setting(tenant.id, "catalog", "")}


class ManualCatalog(BaseModel):
    text: str


@router.post("/manual")
def save_manual(data: ManualCatalog, tenant: Tenant = Depends(require_tenant)):
    save_setting(tenant.id, "catalog", data.text)
    return {"status": "ok"}


class BusinessConfig(BaseModel):
    business_name: str
    hours: str
    yape_number: str = ""
    yape_name: str = ""
    plin_number: str = ""
    culqi_link: str = ""
    owner_whatsapp: str = ""


@router.post("/config")
def save_config(cfg: BusinessConfig, tenant: Tenant = Depends(require_tenant)):
    save_setting(tenant.id, "business_name", cfg.business_name)
    save_setting(tenant.id, "hours", cfg.hours)
    save_setting(tenant.id, "yape_number", cfg.yape_number)
    save_setting(tenant.id, "yape_name", cfg.yape_name)
    save_setting(tenant.id, "plin_number", cfg.plin_number)
    save_setting(tenant.id, "culqi_link", cfg.culqi_link)
    save_setting(tenant.id, "owner_whatsapp", cfg.owner_whatsapp)
    return {"status": "ok"}


@router.get("/config")
def get_config(tenant: Tenant = Depends(require_tenant)):
    return {
        "business_name":   get_setting(tenant.id, "business_name", "Mi Negocio"),
        "hours":           get_setting(tenant.id, "hours", "Lunes a sábado 9am-7pm"),
        "yape_number":     get_setting(tenant.id, "yape_number", ""),
        "yape_name":       get_setting(tenant.id, "yape_name", ""),
        "plin_number":     get_setting(tenant.id, "plin_number", ""),
        "culqi_link":      get_setting(tenant.id, "culqi_link", ""),
        "owner_whatsapp":  get_setting(tenant.id, "owner_whatsapp", ""),
    }
