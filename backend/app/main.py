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


@app.delete("/admin/cleanup-duplicate-tenants")
def cleanup_duplicate_tenants():
    """Remove duplicate tenants keeping only the one with a real phone number per slug."""
    from .database import (SessionLocal, Tenant, Message, Order,
                           TenantSetting, CustomerSession, MessageBuffer, Interest)
    from sqlalchemy import func, text as _text
    deleted = []
    with SessionLocal() as db:
        slugs = [r[0] for r in db.query(Tenant.slug).group_by(Tenant.slug).having(func.count() > 1).all()]
        for slug in slugs:
            dupes = db.query(Tenant).filter(Tenant.slug == slug).order_by(Tenant.created_at).all()
            def score(t):
                is_real = 0 if t.phone_number.startswith("sandbox:") else 1
                msg_count = db.query(Message).filter(Message.tenant_id == t.id).count()
                return (is_real, msg_count)
            dupes_sorted = sorted(dupes, key=score, reverse=True)
            keep = dupes_sorted[0]
            for t in dupes_sorted[1:]:
                tid = t.id
                db.query(Message).filter(Message.tenant_id == tid).delete()
                db.query(Order).filter(Order.tenant_id == tid).delete()
                db.query(TenantSetting).filter(TenantSetting.tenant_id == tid).delete()
                db.query(CustomerSession).filter(CustomerSession.tenant_id == tid).delete()
                db.query(MessageBuffer).filter(MessageBuffer.tenant_id == tid).delete()
                db.query(Interest).filter(Interest.tenant_id == tid).delete()
                db.delete(t)
                deleted.append({"deleted": tid[:8], "kept": keep.id[:8]})
        db.commit()
    return {"deleted": deleted}
