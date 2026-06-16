from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from ..services.ocr import extract_text_from_pdf, extract_text_from_image
from ..database import save_catalog, get_catalog, save_business_setting, get_business_setting

router = APIRouter(prefix="/catalog")

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}


@router.post("/upload")
async def upload_catalog(file: UploadFile = File(...)):
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

    save_catalog(text)
    save_business_setting("catalog", text)
    return {"status": "ok", "characters": len(text), "preview": text[:500]}


@router.get("/")
def get_current_catalog():
    return {"catalog": get_business_setting("catalog", get_catalog())}


class ManualCatalog(BaseModel):
    text: str


@router.post("/manual")
def save_manual(data: ManualCatalog):
    save_business_setting("catalog", data.text)
    return {"status": "ok"}


class BusinessConfig(BaseModel):
    business_name: str
    hours: str


@router.post("/config")
def save_config(cfg: BusinessConfig):
    save_business_setting("business_name", cfg.business_name)
    save_business_setting("hours", cfg.hours)
    return {"status": "ok"}


@router.get("/config")
def get_config():
    return {
        "business_name": get_business_setting("business_name", "Mi Negocio"),
        "hours": get_business_setting("hours", "Lunes a sábado 9am-7pm"),
    }
