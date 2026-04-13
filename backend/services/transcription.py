import os
from groq import AsyncGroq

async def transcribe_audio(audio_path: str) -> str:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    with open(audio_path, "rb") as f:
        res = await client.audio.transcriptions.create(model="whisper-large-v3", file=f, language="bg")
    return res.text

