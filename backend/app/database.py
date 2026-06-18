import os
import uuid
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///respondIA.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)  # whatsapp:+1xxx
    api_key = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    plan = Column(String, default="basic")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class TenantSetting(Base):
    __tablename__ = "tenant_settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    customer = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    ts = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)   # "#0001"
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    customer = Column(String, nullable=False)             # whatsapp:+51xxx
    items = Column(Text, nullable=False)                  # descripción libre
    total = Column(Integer, nullable=False)               # soles
    status = Column(String, default="pendiente")          # pendiente|pagado|enviado|entregado
    created_at = Column(DateTime, server_default=func.now())


def init_db():
    Base.metadata.create_all(engine)


# --- Tenant ---

def get_tenant_by_phone(phone: str) -> Tenant | None:
    with SessionLocal() as db:
        return db.query(Tenant).filter(
            Tenant.phone_number == phone,
            Tenant.is_active == True
        ).first()


def get_tenant_by_api_key(api_key: str) -> Tenant | None:
    with SessionLocal() as db:
        return db.query(Tenant).filter(Tenant.api_key == api_key).first()


def create_tenant(name: str, phone_number: str) -> Tenant:
    with SessionLocal() as db:
        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name,
            phone_number=phone_number,
            api_key=str(uuid.uuid4()),
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        # detach from session so it can be used outside
        db.expunge(tenant)
        return tenant


def list_tenants() -> list[Tenant]:
    with SessionLocal() as db:
        tenants = db.query(Tenant).all()
        for t in tenants:
            db.expunge(t)
        return tenants


# --- Messages ---

def save_message(tenant_id: str, customer: str, user_msg: str, bot_msg: str):
    with SessionLocal() as db:
        db.add(Message(tenant_id=tenant_id, customer=customer, role="user", content=user_msg))
        db.add(Message(tenant_id=tenant_id, customer=customer, role="assistant", content=bot_msg))
        db.commit()


def save_owner_message(tenant_id: str, customer: str, text: str):
    with SessionLocal() as db:
        db.add(Message(tenant_id=tenant_id, customer=customer, role="owner", content=text))
        db.commit()


def get_history(tenant_id: str, customer: str, limit: int = 8) -> list[dict]:
    with SessionLocal() as db:
        rows = db.query(Message).filter(
            Message.tenant_id == tenant_id,
            Message.customer == customer,
        ).order_by(Message.ts.desc()).limit(limit).all()
        return [{"role": r.role, "content": r.content} for r in reversed(rows)]


def get_all_messages(tenant_id: str) -> list[dict]:
    with SessionLocal() as db:
        rows = db.query(Message).filter(
            Message.tenant_id == tenant_id
        ).order_by(Message.ts.desc()).limit(200).all()
        return [
            {"customer": r.customer, "role": r.role, "content": r.content, "ts": str(r.ts)}
            for r in rows
        ]


# --- Settings ---

def get_setting(tenant_id: str, key: str, default: str = "") -> str:
    with SessionLocal() as db:
        row = db.query(TenantSetting).filter(
            TenantSetting.tenant_id == tenant_id,
            TenantSetting.key == key,
        ).first()
        return row.value if row else default


def save_setting(tenant_id: str, key: str, value: str):
    with SessionLocal() as db:
        row = db.query(TenantSetting).filter(
            TenantSetting.tenant_id == tenant_id,
            TenantSetting.key == key,
        ).first()
        if row:
            row.value = value
        else:
            db.add(TenantSetting(tenant_id=tenant_id, key=key, value=value))
        db.commit()


# --- Orders ---

def _next_order_code(db, tenant_id: str) -> str:
    count = db.query(Order).filter(Order.tenant_id == tenant_id).count()
    return f"#{str(count + 1).zfill(4)}"


def create_order(tenant_id: str, customer: str, items: str, total: int) -> Order:
    with SessionLocal() as db:
        code = _next_order_code(db, tenant_id)
        order = Order(code=code, tenant_id=tenant_id, customer=customer,
                      items=items, total=total)
        db.add(order)
        db.commit()
        db.refresh(order)
        db.expunge(order)
        return order


def get_orders(tenant_id: str) -> list[Order]:
    with SessionLocal() as db:
        orders = db.query(Order).filter(
            Order.tenant_id == tenant_id
        ).order_by(Order.created_at.desc()).all()
        for o in orders:
            db.expunge(o)
        return orders


def update_order_status(order_id: int, tenant_id: str, status: str) -> bool:
    with SessionLocal() as db:
        order = db.query(Order).filter(
            Order.id == order_id, Order.tenant_id == tenant_id
        ).first()
        if not order:
            return False
        order.status = status
        db.commit()
        return True


def get_pending_order(tenant_id: str, customer: str) -> Order | None:
    """Returns the most recent pending order for a customer."""
    with SessionLocal() as db:
        order = db.query(Order).filter(
            Order.tenant_id == tenant_id,
            Order.customer == customer,
            Order.status == "pendiente",
        ).order_by(Order.created_at.desc()).first()
        if order:
            db.expunge(order)
        return order


def mark_order_paid(order_id: int) -> None:
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = "pagado"
            db.commit()
