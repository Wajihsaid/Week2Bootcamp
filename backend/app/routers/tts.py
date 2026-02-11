"""
TTS Router - Text-to-Speech with Character Voices (gTTS fallback)
"""

import tempfile
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from gtts import gTTS

from app.models.schemas import TTSRequest
from app.config import CHARACTER_VOICES

router = APIRouter()


@router.post("/tts")
async def text_to_speech(tts_request: TTSRequest):
    """
    Convert text to speech with character-inspired voice settings.
    Uses gTTS (Google Text-to-Speech) to generate MP3.
    """
    try:
        text = tts_request.text
        character_id = tts_request.characterId

        # Pick language (default English). You can map per character if needed.
        lang = "en"

        logger.info(f"TTS request: character={character_id}, text_length={len(text)}")

        # Create temporary MP3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            output_path = temp_file.name

        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)

        logger.info(f"TTS generated: {output_path}")

        # Return audio file
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename="speech.mp3",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tts/voices")
async def list_voices():
    """List available character voice settings (informational)."""
    return {
        "voices": CHARACTER_VOICES
    }
