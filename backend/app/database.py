import os
import re
import uuid
import unicodedata
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey, Boolean, text, UniqueConstraint
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
    phone_number = Column(String, unique=True, nullable=False)  # whatsapp:+1xxx or sandbox:{uuid}
    slug = Column(String, unique=True, nullable=True)           # keyword for sandbox routing, e.g. "NABILA"
    api_key = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    plan = Column(String, default="basic")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class CustomerSession(Base):
    """Maps a customer's WhatsApp number to a tenant in sandbox mode."""
    __tablename__ = "customer_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer = Column(String, nullable=False, index=True)   # whatsapp:+51xxx
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    last_seen = Column(DateTime, server_default=func.now(), onupdate=func.now())


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


def _generate_slug(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Z0-9]", "", ascii_str.upper())
    return (slug[:12] or "NEGOCIO")


def _unique_slug(db, base: str) -> str:
    candidate = base
    while db.query(Tenant).filter(Tenant.slug == candidate).first():
        candidate = base[:8] + uuid.uuid4().hex[:4].upper()
    return candidate


def init_db():
    Base.metadata.create_all(engine)
    # Add new columns to existing tables without Alembic
    is_pg = DATABASE_URL.startswith("postgresql")
    with engine.begin() as conn:
        for col, typ in [
            ("email", "VARCHAR"),
            ("hashed_password", "VARCHAR"),
            ("slug", "VARCHAR"),
        ]:
            try:
                if is_pg:
                    conn.execute(text(f"ALTER TABLE tenants ADD COLUMN IF NOT EXISTS {col} {typ}"))
                else:
                    conn.execute(text(f"ALTER TABLE tenants ADD COLUMN {col} {typ}"))
            except Exception:
                pass

    # Backfill NULL is_active → True for tenants created before the column existed
    with engine.begin() as conn:
        conn.execute(text("UPDATE tenants SET is_active = true WHERE is_active IS NULL"))

    # Add followed_up_at to interests if missing
    with engine.begin() as conn:
        try:
            if DATABASE_URL.startswith("postgresql"):
                conn.execute(text("ALTER TABLE interests ADD COLUMN IF NOT EXISTS followed_up_at TIMESTAMP"))
            else:
                conn.execute(text("ALTER TABLE interests ADD COLUMN followed_up_at TIMESTAMP"))
        except Exception:
            pass

    # Backfill slugs for existing tenants that don't have one
    with SessionLocal() as db:
        for tenant in db.query(Tenant).filter(Tenant.slug == None).all():
            tenant.slug = _unique_slug(db, _generate_slug(tenant.name))
        db.commit()


# --- Tenant ---

def get_tenant_by_phone(phone: str) -> Tenant | None:
    with SessionLocal() as db:
        return db.query(Tenant).filter(
            Tenant.phone_number == phone,
        ).first()


def get_tenant_by_api_key(api_key: str) -> Tenant | None:
    with SessionLocal() as db:
        return db.query(Tenant).filter(Tenant.api_key == api_key).first()


def get_tenant_by_id(tenant_id: str) -> Tenant | None:
    with SessionLocal() as db:
        t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if t:
            db.expunge(t)
        return t


def get_tenant_by_slug(slug: str) -> Tenant | None:
    with SessionLocal() as db:
        t = db.query(Tenant).filter(Tenant.slug == slug.upper()).first()
        if t:
            db.expunge(t)
        return t


def create_tenant(name: str, phone_number: str,
                  email: str = None, hashed_password: str = None,
                  slug: str = None) -> Tenant:
    with SessionLocal() as db:
        final_slug = _unique_slug(db, slug or _generate_slug(name))
        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name,
            phone_number=phone_number,
            slug=final_slug,
            api_key=str(uuid.uuid4()),
            email=email,
            hashed_password=hashed_password,
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        db.expunge(tenant)
        return tenant


def get_tenant_by_email(email: str):
    with SessionLocal() as db:
        t = db.query(Tenant).filter(Tenant.email == email).first()
        if t:
            db.expunge(t)
        return t


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


# --- Interests (leads) ---

class Interest(Base):
    __tablename__ = "interests"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id      = Column(String, ForeignKey("tenants.id"), nullable=False)
    customer       = Column(String, nullable=False)
    last_product   = Column(String, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now())
    followed_up_at = Column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint("tenant_id", "customer"),)


def upsert_interest(tenant_id: str, customer: str, product_hint: str = "") -> None:
    with SessionLocal() as db:
        row = db.query(Interest).filter(
            Interest.tenant_id == tenant_id,
            Interest.customer  == customer,
        ).first()
        if row:
            if product_hint:
                row.last_product = product_hint[:120]
        else:
            db.add(Interest(tenant_id=tenant_id, customer=customer,
                            last_product=product_hint[:120] if product_hint else ""))
        db.commit()


def delete_interest(tenant_id: str, customer: str) -> None:
    with SessionLocal() as db:
        db.query(Interest).filter(
            Interest.tenant_id == tenant_id,
            Interest.customer  == customer,
        ).delete()
        db.commit()


def get_interests(tenant_id: str) -> list:
    with SessionLocal() as db:
        rows = db.query(Interest).filter(
            Interest.tenant_id == tenant_id
        ).order_by(Interest.updated_at.desc()).all()
        for r in rows:
            db.expunge(r)
        return rows


def get_stale_interests(tenant_id: str, min_days: int = 3) -> list:
    """Interests older than min_days with no follow-up sent yet."""
    from datetime import timedelta
    with SessionLocal() as db:
        cutoff = datetime.utcnow() - timedelta(days=min_days)
        rows = db.query(Interest).filter(
            Interest.tenant_id == tenant_id,
            Interest.updated_at <= cutoff,
            Interest.followed_up_at == None,
        ).all()
        for r in rows:
            db.expunge(r)
        return rows


def mark_followed_up(tenant_id: str, customer: str) -> None:
    with SessionLocal() as db:
        row = db.query(Interest).filter(
            Interest.tenant_id == tenant_id,
            Interest.customer  == customer,
        ).first()
        if row:
            row.followed_up_at = datetime.utcnow()
            db.commit()


# --- Message Buffer (debouncing) ---

class MessageBuffer(Base):
    __tablename__ = "message_buffers"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    customer      = Column(String, nullable=False, index=True)
    tenant_id     = Column(String, ForeignKey("tenants.id"), nullable=False)
    messages      = Column(Text, nullable=False, default="[]")   # JSON list
    last_received_at = Column(DateTime, nullable=False)


def append_to_buffer(customer: str, tenant_id: str, message: str, received_at) -> None:
    import json
    with SessionLocal() as db:
        buf = db.query(MessageBuffer).filter(
            MessageBuffer.customer  == customer,
            MessageBuffer.tenant_id == tenant_id,
        ).first()
        if buf:
            msgs = json.loads(buf.messages or "[]")
            msgs.append(message)
            buf.messages = json.dumps(msgs)
            buf.last_received_at = received_at
        else:
            db.add(MessageBuffer(
                customer=customer,
                tenant_id=tenant_id,
                messages=json.dumps([message]),
                last_received_at=received_at,
            ))
        db.commit()


def get_and_clear_buffer(customer: str, tenant_id: str, expected_time) -> list | None:
    """Return buffered messages only if no newer message arrived; clears the buffer."""
    import json
    with SessionLocal() as db:
        buf = db.query(MessageBuffer).filter(
            MessageBuffer.customer  == customer,
            MessageBuffer.tenant_id == tenant_id,
        ).first()
        if not buf:
            return None
        # If a newer message arrived (last_received_at > expected_time + 1s), abort
        diff = (buf.last_received_at - expected_time).total_seconds()
        if diff > 1:
            return None
        msgs = json.loads(buf.messages or "[]")
        db.delete(buf)
        db.commit()
        return msgs


# --- Customer Sessions (sandbox routing) ---

def get_customer_session(customer: str) -> CustomerSession | None:
    with SessionLocal() as db:
        s = db.query(CustomerSession).filter(
            CustomerSession.customer == customer
        ).first()
        if s:
            db.expunge(s)
        return s


def upsert_customer_session(customer: str, tenant_id: str) -> None:
    with SessionLocal() as db:
        s = db.query(CustomerSession).filter(CustomerSession.customer == customer).first()
        if s:
            s.tenant_id = tenant_id
        else:
            db.add(CustomerSession(customer=customer, tenant_id=tenant_id))
        db.commit()


# --- Orders ---

def _next_order_code(db, tenant_id: str) -> str:
    count = db.query(Order).filter(Order.tenant_id == tenant_id).count()
    suffix = uuid.uuid4().hex[:4]
    return f"#{str(count + 1).zfill(4)}-{suffix}"


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
