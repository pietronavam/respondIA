import os
import base64
import httpx
import anthropic

_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


async def verify_payment_screenshot(
    image_url: str,
    twilio_sid: str,
    twilio_token: str,
    expected_total: int,
    yape_number: str = "",
    plin_number: str = "",
) -> tuple[bool, str]:
    """
    Downloads the Twilio image and asks Claude Vision whether it's a valid
    Yape/Plin payment for the expected amount.

    Returns (verified: bool, reason: str)
    """
    # Download image from Twilio (requires Basic auth)
    try:
        async with httpx.AsyncClient(timeout=15) as http:
            r = await http.get(image_url, auth=(twilio_sid, twilio_token))
            r.raise_for_status()
            image_b64 = base64.standard_b64encode(r.content).decode()
            media_type = r.headers.get("content-type", "image/jpeg").split(";")[0]
    except Exception as e:
        return False, f"No se pudo descargar la imagen: {e}"

    # Build context for Claude
    recipients = []
    if yape_number:
        recipients.append(f"Yape: {yape_number}")
    if plin_number:
        recipients.append(f"Plin: {plin_number}")
    recipient_str = " o ".join(recipients) if recipients else "el número del negocio"

    prompt = f"""Analiza esta imagen. Es una supuesta captura de pantalla de pago por Yape o Plin.

Verifica:
1. ¿Es un comprobante real de Yape o Plin (no una foto de otra cosa)?
2. ¿El monto pagado es S/{expected_total}? (puede variar ±1 sol por redondeo)
3. ¿El destinatario coincide con {recipient_str}? (si no hay número visible, acepta igualmente)

Responde ÚNICAMENTE con este formato JSON:
{{"verificado": true/false, "motivo": "explicación breve en español"}}"""

    try:
        msg = _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=120,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        import json, re
        raw = msg.content[0].text.strip()
        # Extract JSON even if surrounded by markdown
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return bool(data.get("verificado")), data.get("motivo", "")
        return False, "Respuesta inesperada del verificador"
    except Exception as e:
        return False, f"Error al verificar: {e}"
