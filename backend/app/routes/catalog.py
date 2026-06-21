from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from ..auth import require_tenant
from ..database import Tenant, save_setting, get_setting, get_interests
from ..services.ocr import extract_text_from_pdf, extract_text_from_image

router = APIRouter(prefix="/catalog")


def _trigger_price_drop_alerts(tenant: Tenant, old_catalog: str, new_catalog: str):
    from ..services.followup_service import process_price_drop_alerts, SANDBOX_FROM
    interests = get_interests(tenant.id)
    if not interests:
        return
    business_name = get_setting(tenant.id, "business_name") or tenant.name
    phone = tenant.phone_number or ""
    from_wa = phone if (phone.startswith("whatsapp:") and "sandbox" not in phone) else SANDBOX_FROM
    count = process_price_drop_alerts(
        tenant_id=tenant.id,
        old_catalog=old_catalog,
        new_catalog=new_catalog,
        business_name=business_name,
        from_wa=from_wa,
        interests=interests,
    )
    if count:
        print(f"[PRICE DROP] Sent {count} alert(s) for tenant {tenant.id}")

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}


@router.post("/upload")
async def upload_catalog(
    background_tasks: BackgroundTasks,
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

    old_catalog = get_setting(tenant.id, "catalog") or ""
    save_setting(tenant.id, "catalog", text)
    if old_catalog:
        background_tasks.add_task(_trigger_price_drop_alerts, tenant, old_catalog, text)
    return {"status": "ok", "characters": len(text), "preview": text[:500]}


@router.get("/")
def get_current_catalog(tenant: Tenant = Depends(require_tenant)):
    return {"catalog": get_setting(tenant.id, "catalog", "")}


class ManualCatalog(BaseModel):
    text: str


@router.post("/manual")
def save_manual(data: ManualCatalog, background_tasks: BackgroundTasks, tenant: Tenant = Depends(require_tenant)):
    old_catalog = get_setting(tenant.id, "catalog") or ""
    save_setting(tenant.id, "catalog", data.text)
    if old_catalog:
        background_tasks.add_task(_trigger_price_drop_alerts, tenant, old_catalog, data.text)
    return {"status": "ok"}


class BusinessConfig(BaseModel):
    business_name: str
    hours: str
    yape_number: str = ""
    yape_name: str = ""
    plin_number: str = ""
    culqi_link: str = ""
    owner_whatsapp: str = ""
    followup_enabled: bool = False
    followup_days: int = 3


@router.post("/config")
def save_config(cfg: BusinessConfig, tenant: Tenant = Depends(require_tenant)):
    save_setting(tenant.id, "business_name", cfg.business_name)
    save_setting(tenant.id, "hours", cfg.hours)
    save_setting(tenant.id, "yape_number", cfg.yape_number)
    save_setting(tenant.id, "yape_name", cfg.yape_name)
    save_setting(tenant.id, "plin_number", cfg.plin_number)
    save_setting(tenant.id, "culqi_link", cfg.culqi_link)
    save_setting(tenant.id, "owner_whatsapp", cfg.owner_whatsapp)
    save_setting(tenant.id, "followup_enabled", "1" if cfg.followup_enabled else "0")
    save_setting(tenant.id, "followup_days", str(max(1, cfg.followup_days)))
    return {"status": "ok"}


@router.get("/config")
def get_config(tenant: Tenant = Depends(require_tenant)):
    return {
        "business_name":    get_setting(tenant.id, "business_name", "Mi Negocio"),
        "hours":            get_setting(tenant.id, "hours", "Lunes a sábado 9am-7pm"),
        "yape_number":      get_setting(tenant.id, "yape_number", ""),
        "yape_name":        get_setting(tenant.id, "yape_name", ""),
        "plin_number":      get_setting(tenant.id, "plin_number", ""),
        "culqi_link":       get_setting(tenant.id, "culqi_link", ""),
        "owner_whatsapp":   get_setting(tenant.id, "owner_whatsapp", ""),
        "followup_enabled": get_setting(tenant.id, "followup_enabled", "0") == "1",
        "followup_days":    int(get_setting(tenant.id, "followup_days", "3")),
    }
