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

    detail_parts = []
    if talla:
        detail_parts.append(f"talla {talla}")
    if color:
        detail_parts.append(f"color {color}")
    detail = f" ({', '.join(detail_parts)})" if detail_parts else ""

    prompt = f"""Eres el asistente de ventas de *{business_name}* en WhatsApp.
Un cliente mostró interés en *{product}{detail}* hace {days_since} días pero no concretó la compra.

Contexto actual: {season_ctx}.

Catálogo relevante:
{catalog_snippet[:400] if catalog_snippet else "Sin detalle adicional."}

Tu tarea: escribe UN mensaje de WhatsApp corto (máximo 3 líneas) para reconquistar a este cliente.

Criterios:
- Si la temporada actual es relevante para el producto (ej: shorts en verano, abrigos en invierno), úsala creativamente.
- Si no es relevante, busca OTRO ángulo persuasivo: escasez ("quedan pocas unidades"), exclusividad, precio, o un tono cálido/divertido.
- No forces el contexto estacional si no encaja.
- Sé creativo, natural, breve. Tono amigable, no invasivo.
- Usa formato WhatsApp: *negrita* con asterisco simple. Sin listas.
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
