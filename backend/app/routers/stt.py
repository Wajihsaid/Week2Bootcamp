"""
STT Router - Speech-to-Text (lazy import)
"""

import tempfile
import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from loguru import logger

from app.models.schemas import STTResponse

router = APIRouter()


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(file: UploadFile = File(...)):
    """
    Convert speech to text from uploaded audio file.
    Lazily imports SpeechRecognition to avoid startup failure when not installed.
    """
    try:
        try:
            import speech_recognition as sr  # lazy import
        except Exception as e:
            logger.error(f"SpeechRecognition not available: {e}")
            raise HTTPException(status_code=503, detail="Speech recognition module is not installed.")

        logger.info(f"STT request: filename={file.filename}, content_type={file.content_type}")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Initialize recognizer
            recognizer = sr.Recognizer()

            # Convert audio file to AudioFile
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)

            # Recognize speech using Google Speech Recognition
            try:
                text = recognizer.recognize_google(audio)
                logger.info(f"STT result: {text[:100]}")

                return STTResponse(
                    text=text,
                    confidence=None,
                    language="en-US"
                )

            except sr.UnknownValueError:
                raise HTTPException(status_code=400, detail="Could not understand audio")
            except sr.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Speech recognition service error: {e}")

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stt/info")
async def stt_info():
    """Get information about STT service."""
    return {
        "service": "Google Speech Recognition",
        "supported_formats": ["wav", "mp3", "flac", "ogg"],
        "max_file_size": "10MB",
        "language": "en-US"
    }
