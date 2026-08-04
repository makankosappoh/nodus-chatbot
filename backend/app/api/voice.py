"""
app/api/voice.py
----------------
POST /api/voice/transcribe — converts audio to text using Groq Whisper
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Receives audio file from frontend microphone.
    Returns transcribed text via Groq Whisper.
    """
    try:
        client = Groq(api_key=settings.groq_api_key)
        
        audio_bytes = await audio.read()
        
        transcription = client.audio.transcriptions.create(
            file=(audio.filename or "audio.webm", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="en",
        )
        
        logger.info(f"Transcribed: {transcription[:60]}")
        return {"text": transcription}
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))