import tempfile
import os
import httpx

_model = None


def _get_model():
    global _model
    if _model is None:
        import whisper
        _model = whisper.load_model("base")
    return _model


async def transcribe_audio_url(audio_url: str, account_sid: str, auth_token: str) -> str:
    """Download Twilio audio (requires auth) and transcribe with Whisper."""
    async with httpx.AsyncClient() as client:
        response = await client.get(audio_url, auth=(account_sid, auth_token))
        response.raise_for_status()

    # Twilio sends .ogg for WhatsApp voice notes
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        model = _get_model()
        result = model.transcribe(tmp_path, language="es")
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)
