import os
import re
import json
from openai import OpenAI
from ..database import get_history, get_setting

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM_TEMPLATE = """Eres el asistente virtual de {business_name}, atendiendo clientes por WhatsApp.
Responde de forma amigable, breve y directa (máximo 3-4 líneas por mensaje).

CATÁLOGO Y SERVICIOS DEL NEGOCIO:
{catalog}

HORARIO DE ATENCIÓN:
{hours}

PAGOS:
{payment_info}

REGLAS GENERALES:
- Responde siempre en español peruano natural
- Si un producto no está en el catálogo, dilo honestamente
- Usa emojis con moderación (1-2 por mensaje máximo)
- Si no puedes resolver algo, ofrece escalar con el dueño

REGLAS PARA PEDIDOS:
Cuando un cliente confirme qué producto(s) quiere comprar:
1. Confirma el producto, talla/color si aplica, y calcula el total (producto + envío si lo menciona)
2. En ESA MISMA respuesta envía las instrucciones de pago (Yape/Plin/link disponibles)
3. Pide la foto del comprobante de pago
4. OBLIGATORIO: al FINAL de esa misma respuesta agrega EXACTAMENTE esta línea (sin mostrarla al cliente):
   [PEDIDO:{"items":"{items_placeholder}","total":{total_placeholder}}]
   - items = descripción breve del pedido (ej: "1 blusa floreada talla L negro")
   - total = monto total en soles como número entero (ej: 55)
   - NO omitas este marcador bajo ninguna circunstancia cuando confirmes un pedido

Cuando el cliente mande foto de comprobante de pago, responde que ya lo recibiste y que procederás con el envío.
"""

ORDER_RE = re.compile(r'\[PEDIDO:(\{.*?\})\]', re.DOTALL)


async def get_bot_response(
    user_message: str, customer_id: str, tenant_id: str
) -> tuple[str, dict | None]:
    """Returns (visible_reply, order_data | None)"""
    catalog = get_setting(tenant_id, "catalog", "Sin catálogo cargado aún.")
    business_name = get_setting(tenant_id, "business_name", "el negocio")
    hours = get_setting(tenant_id, "hours", "Lunes a sábado 9am-7pm")
    yape_number = get_setting(tenant_id, "yape_number", "")
    plin_number = get_setting(tenant_id, "plin_number", "")
    culqi_link = get_setting(tenant_id, "culqi_link", "")

    payment_lines = []
    if yape_number:
        payment_lines.append(f"- Yape: {yape_number}")
    if plin_number:
        payment_lines.append(f"- Plin: {plin_number}")
    if culqi_link:
        payment_lines.append(f"- Link de pago con tarjeta: {culqi_link}")
    if not payment_lines:
        payment_lines.append("- (Sin método de pago configurado aún)")
    payment_info = "\n".join(payment_lines)

    system = (SYSTEM_TEMPLATE
        .replace("{business_name}", business_name)
        .replace("{catalog}", catalog)
        .replace("{hours}", hours)
        .replace("{payment_info}", payment_info)
        .replace("{items_placeholder}", "ITEMS_DEL_PEDIDO")
        .replace("{total_placeholder}", "0")
    )

    raw_history = get_history(tenant_id, customer_id, limit=8)
    history = [
        {**msg, "role": "assistant"} if msg.get("role") == "owner" else msg
        for msg in raw_history
    ]
    messages = [{"role": "system", "content": system}] + history + [
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=400,
        )
        raw = response.choices[0].message.content or ""
    except Exception:
        return "En este momento no puedo responder. Por favor intenta en unos minutos.", None

    order_data = None
    match = ORDER_RE.search(raw)
    if match:
        try:
            order_data = json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
        raw = ORDER_RE.sub("", raw).strip()

    return raw, order_data
