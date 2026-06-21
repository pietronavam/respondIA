import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import webhook, catalog, conversations, tenants, orders, register, login

CRON_SECRET = os.getenv("CRON_SECRET", "")

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


@app.post("/admin/process-followups")
async def process_followups_cron(x_cron_secret: str = Header(None)):
    """Called daily by cron-job.org. Sends auto followups to stale interests."""
    if CRON_SECRET and x_cron_secret != CRON_SECRET:
        raise HTTPException(403, "Unauthorized")

    import asyncio
    import json
    from datetime import datetime
    from .database import (
        list_tenants, get_setting, get_stale_interests, mark_followed_up,
    )
    from .services.followup_service import generate_followup_message, send_followup, SANDBOX_FROM

    results = []
    for tenant in list_tenants():
        if get_setting(tenant.id, "followup_enabled", "0") != "1":
            continue
        days = int(get_setting(tenant.id, "followup_days", "3"))
        stale = get_stale_interests(tenant.id, min_days=days)
        if not stale:
            continue

        business_name = get_setting(tenant.id, "business_name") or tenant.name
        catalog_text  = get_setting(tenant.id, "catalog") or ""
        phone = tenant.phone_number or ""
        from_wa = phone if (phone.startswith("whatsapp:") and "sandbox" not in phone) else SANDBOX_FROM

        for interest in stale:
            raw = interest.last_product or ""
            try:
                d = json.loads(raw)
                product = d.get("product", "") or "producto"
                talla   = d.get("talla", "")
                color   = d.get("color", "")
            except Exception:
                product, talla, color = raw or "producto", "", ""

            days_since = (datetime.utcnow() - interest.updated_at).days if interest.updated_at else 0

            message = await asyncio.to_thread(
                generate_followup_message,
                business_name=business_name,
                product=product, talla=talla, color=color,
                days_since=days_since, catalog_snippet=catalog_text,
            )
            sent = await asyncio.to_thread(send_followup, interest.customer, message, from_wa)
            if sent:
                mark_followed_up(tenant.id, interest.customer)
                results.append({"tenant": tenant.name, "customer": interest.customer})

    return {"processed": len(results), "results": results}


