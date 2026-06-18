from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import webhook, catalog, conversations, tenants, orders, register

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


@app.get("/")
def root():
    return {"status": "RespondIA backend running", "version": "0.2.0"}


@app.get("/health")
def health():
    return {"ok": True}
