from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import webhook, catalog, conversations, tenants, orders, register, login

app = FastAPI(title="RespondIA API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(webhook.router)
app.include_router(catalog.router)
app.include_router(conversations.router)
app.include_router(tenants.router)
app.include_router(orders.router)
app.include_router(register.router)
app.include_router(login.router)


@app.get("/")
def root():
    return {"status": "RespondIA backend running", "version": "0.2.0"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/debug/tenant/{phone}")
def debug_tenant(phone: str):
    from .database import get_tenant_by_phone, get_tenant_by_slug, SessionLocal, Tenant
    t_phone = get_tenant_by_phone(f"whatsapp:{phone}")
    t_slug  = get_tenant_by_slug("NABILAHOME")
    with SessionLocal() as db:
        all_t = db.query(Tenant).all()
        tenants_info = [{"id": t.id[:8], "name": t.name, "slug": t.slug, "is_active": t.is_active} for t in all_t]
    return {
        "by_phone": {"id": t_phone.id[:8], "name": t_phone.name} if t_phone else None,
        "by_slug":  {"id": t_slug.id[:8],  "name": t_slug.name}  if t_slug  else None,
        "all_tenants": tenants_info,
    }
