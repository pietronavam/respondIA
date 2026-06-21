import os
from datetime import datetime
from openai import OpenAI
from twilio.rest import Client as TwilioClient

_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SANDBOX_FROM = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "")

_MONTH_CONTEXT = {
    12: "diciembre, época navideña y de verano en Perú",
    1:  "enero, verano en Perú, playa y calor",
    2:  "febrero, verano en Perú, temporada de playa",
    3:  "marzo, fin del verano, temperaturas altas",
    4:  "abril, otoño, clima cambiante",
    5:  "mayo, otoño, clima fresco",
    6:  "junio, invierno en Lima, garúa y frío húmedo",
    7:  "julio, invierno, Fiestas Patrias",
    8:  "agosto, invierno, viento y frío en Lima",
    9:  "septiembre, primavera, clima mejorando",
    10: "octubre, primavera, días más cálidos",
    11: "noviembre, pre-verano, temperaturas subiendo",
}


def generate_followup_message(
    business_name: str,
    product: str,
    talla: str = "",
    color: str = "",
    days_since: int = 0,
    catalog_snippet: str = "",
) -> str:
    month = datetime.utcnow().month
    season_ctx = _MONTH_CONTEXT.get(month, "")

    detail = f" ({color})" if color else ""

    prompt = f"""Eres el asistente de ventas de *{business_name}* en WhatsApp.
Un cliente mostró interés en *{product}{detail}* hace {days_since} días pero no concretó la compra.

Contexto actual: {season_ctx}.

Catálogo relevante:
{catalog_snippet[:400] if catalog_snippet else "Sin detalle adicional."}

Tu tarea: escribe UN mensaje de WhatsApp corto (máximo 3 líneas) para reconquistar a este cliente.

Criterios:
- El contexto estacional SOLO es relevante para productos muy específicos: ropa de baño o shorts en verano, casacas o abrigos en invierno. Para jeans, polos, blusas, conjuntos casuales → NO lo uses.
- Si la temporada no aplica claramente, elige OTRO ángulo: escasez ("quedan pocas unidades"), precio especial, estilo o un tono cálido/divertido.
- Sé creativo, natural, breve. Tono amigable, no invasivo.
- Usa formato WhatsApp: *negrita* con asterisco simple. Sin listas.
- NO menciones la talla en el mensaje.
- NO empieces con "Hola" genérico. Engancha desde la primera palabra.
- Termina con una pregunta o llamada a la acción suave.

Responde SOLO con el mensaje, sin comillas ni explicaciones."""

    try:
        resp = _client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[FOLLOWUP LLM ERROR] {e}")
        return (
            f"👋 ¿Aún te interesa el *{product}*? "
            f"Todavía está disponible en *{business_name}*. "
            f"¿Te lo apartamos? 😊"
        )


def send_followup(customer: str, message: str, from_: str = "") -> bool:
    try:
        twilio = TwilioClient(ACCOUNT_SID, AUTH_TOKEN)
        twilio.messages.create(
            body=message,
            from_=from_ or SANDBOX_FROM,
            to=customer,
        )
        return True
    except Exception as e:
        print(f"[FOLLOWUP SEND ERROR] {e}")
        return False


# ── Price-drop alerts ──────────────────────────────────────────────────────────

def detect_price_drops(old_catalog: str, new_catalog: str) -> list[dict]:
    """
    Returns [{product, old_price, new_price}] where new_price < old_price.
    Uses LLM to handle natural-language catalogs.
    """
    prompt = f"""Compara estos dos catálogos de una tienda y encuentra qué productos bajaron de precio.

CATÁLOGO ANTERIOR:
{old_catalog[:1000]}

CATÁLOGO NUEVO:
{new_catalog[:1000]}

Devuelve SOLO JSON con las bajadas de precio (new_price < old_price):
[{{"product": "nombre del producto", "old_price": número, "new_price": número}}]

Si no hay bajadas, devuelve [].
No incluyas productos cuyo precio subió ni los que no cambiaron."""

    try:
        import json, re
        resp = _client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        raw = (resp.choices[0].message.content or "").strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[PRICE DROP DETECT ERROR] {e}")
    return []


def _keywords(text: str) -> set[str]:
    """Lowercase word tokens of length ≥ 3, ignoring accents."""
    import unicodedata, re
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return {w for w in re.findall(r'[a-z]+', text.lower()) if len(w) >= 3}


def find_matching_interests(interests: list, product_name: str) -> list:
    """Returns interests whose product field shares keywords with product_name."""
    import json
    prod_kw = _keywords(product_name)
    matched = []
    for interest in interests:
        raw = interest.last_product or ""
        try:
            d = json.loads(raw)
            candidate = d.get("product", "") or raw
        except Exception:
            candidate = raw
        if prod_kw & _keywords(candidate):
            matched.append(interest)
    return matched


def _fmt(price: float) -> str:
    return f"{price:g}"


def generate_price_drop_message(
    business_name: str,
    product: str,
    old_price: float,
    new_price: float,
    talla: str = "",
    color: str = "",
) -> str:
    detail = f" ({color})" if color else ""
    ahorro = round(old_price - new_price, 2)

    prompt = f"""Eres el asistente de ventas de *{business_name}* en WhatsApp.
El producto *{product}{detail}* acaba de bajar de precio: antes S/{_fmt(old_price)}, ahora S/{_fmt(new_price)} (ahorro de S/{_fmt(ahorro)}).

Un cliente había mostrado interés en este producto pero no compró. Escríbele UN mensaje de WhatsApp corto (máximo 3 líneas) para avisarle de la oferta.

Criterios:
- El precio reducido ES la noticia principal. Úsala como gancho.
- Sé entusiasta pero natural. Tono amigable, no de spam.
- Usa formato WhatsApp: *negrita*. Sin listas.
- Menciona el precio nuevo y lo que se ahorra.
- NO menciones la talla en el mensaje.
- Termina con una llamada a la acción directa.
- NO empieces con "Hola" genérico.

Responde SOLO con el mensaje, sin comillas ni explicaciones."""

    try:
        resp = _client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[PRICE DROP MSG ERROR] {e}")
        return (
            f"🎉 ¡Buenas noticias! El *{product}* que te interesó bajó de S/{_fmt(old_price)} "
            f"a *S/{_fmt(new_price)}*. ¡Ahorras S/{_fmt(ahorro)}! ¿Lo apartamos? 😊"
        )


def process_price_drop_alerts(
    tenant_id: str,
    old_catalog: str,
    new_catalog: str,
    business_name: str,
    from_wa: str,
    interests: list,
) -> int:
    """Detects price drops, finds matching interests, sends alerts. Returns count sent."""
    drops = detect_price_drops(old_catalog, new_catalog)
    if not drops:
        return 0

    sent_count = 0
    from ..database import mark_followed_up

    for drop in drops:
        product   = drop.get("product", "")
        old_price = float(drop.get("old_price", 0))
        new_price = float(drop.get("new_price", 0))
        if not product or old_price <= new_price:
            continue

        matched = find_matching_interests(interests, product)
        for interest in matched:
            message = generate_price_drop_message(
                business_name=business_name,
                product=product,
                old_price=old_price,
                new_price=new_price,
            )
            if send_followup(interest.customer, message, from_wa):
                mark_followed_up(tenant_id, interest.customer)
                sent_count += 1
                print(f"[PRICE DROP] Sent to {interest.customer}: {message[:60]}…")

    return sent_count
