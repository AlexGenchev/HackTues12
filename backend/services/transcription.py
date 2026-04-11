# backend/services/transcription.py
# Speech-to-text transcription using the Groq Whisper API.

import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

from groq import Groq

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)
_RETRY_WAIT_SECONDS = 2


def _transcribe_sync(audio_path: str, client: Groq) -> str:
    """Blocking call to Groq Whisper — runs in a thread pool executor."""
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language="bg",
        )
    return transcript.text


async def transcribe_audio(audio_path: str) -> str:
    """Transcribe a WAV file to Bulgarian text using Groq Whisper.

    Retries once after 2 seconds on failure before raising.
    Raises RuntimeError if transcription fails after retry.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    loop = asyncio.get_event_loop()

    for attempt in range(2):
        try:
            logger.info("Transcription attempt %d for file: %s", attempt + 1, audio_path)
            text = await loop.run_in_executor(
                _executor, _transcribe_sync, audio_path, client
            )
            logger.info("Transcription succeeded (%d chars).", len(text))
            return text
        except Exception as exc:
            logger.error("Transcription attempt %d failed: %s", attempt + 1, exc)
            if attempt == 0:
                await asyncio.sleep(_RETRY_WAIT_SECONDS)

    raise RuntimeError("Groq Whisper transcription failed after retry.")
