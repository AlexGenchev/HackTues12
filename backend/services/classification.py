# backend/services/classification.py
# Complaint classification using the Groq LLM API.
# Classifies transcribed Bulgarian text into a category, extracts the
# location mentioned, and determines urgency level.

import asyncio
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from groq import Groq

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)
_RETRY_WAIT_SECONDS = 2

_SYSTEM_PROMPT = (
    "Ти си система за класифициране на граждански жалби в България. "
    "Анализирай текста и върни само JSON без никакъв допълнителен текст."
)

_USER_PROMPT_TEMPLATE = """Анализирай следната гражданска жалба и върни JSON обект с точно тези ключове:
- "category": една от стойностите: WATER_SUPPLY, ELECTRICITY, ROADS, WASTE_MANAGEMENT, PUBLIC_ORDER, GREEN_SPACES, ADMINISTRATIVE, OTHER
- "location_mentioned": името на града или селото (string), или null ако не е споменато
- "urgency": "HIGH", "MEDIUM" или "LOW" спрямо тона и съдържанието

ЖАЛБА:
{transcribed_text}

Върни САМО JSON без markdown, без обяснения."""

VALID_CATEGORIES = {
    "WATER_SUPPLY",
    "ELECTRICITY",
    "ROADS",
    "WASTE_MANAGEMENT",
    "PUBLIC_ORDER",
    "GREEN_SPACES",
    "ADMINISTRATIVE",
    "OTHER",
}

VALID_URGENCY = {"HIGH", "MEDIUM", "LOW"}


def _classify_sync(transcribed_text: str, client: Groq) -> dict:
    """Blocking LLM call to classify the complaint — runs in thread pool."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _USER_PROMPT_TEMPLATE.format(
                    transcribed_text=transcribed_text
                ),
            },
        ],
        temperature=0.1,
        max_tokens=256,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if the model wraps the JSON
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def _validate_and_normalise(data: dict) -> dict:
    """Validate classification result and normalise to safe defaults."""
    category = data.get("category", "OTHER").upper()
    if category not in VALID_CATEGORIES:
        category = "OTHER"

    urgency = data.get("urgency", "MEDIUM").upper()
    if urgency not in VALID_URGENCY:
        urgency = "MEDIUM"

    location = data.get("location_mentioned")
    if location is not None:
        location = str(location).strip().lower() or None

    return {"category": category, "location_mentioned": location, "urgency": urgency}


async def classify_complaint(transcribed_text: str) -> dict:
    """Classify a Bulgarian complaint text into category, location, and urgency.

    Returns a dict with keys: category, location_mentioned (lowercase str or
    None), urgency.  Retries once after 2 seconds on failure before raising.
    Raises RuntimeError if classification fails after retry.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    loop = asyncio.get_event_loop()

    for attempt in range(2):
        try:
            logger.info("Classification attempt %d.", attempt + 1)
            raw_data = await loop.run_in_executor(
                _executor, _classify_sync, transcribed_text, client
            )
            result = _validate_and_normalise(raw_data)
            logger.info(
                "Classification result: category=%s urgency=%s location=%s",
                result["category"],
                result["urgency"],
                result["location_mentioned"],
            )
            return result
        except Exception as exc:
            logger.error("Classification attempt %d failed: %s", attempt + 1, exc)
            if attempt == 0:
                await asyncio.sleep(_RETRY_WAIT_SECONDS)

    raise RuntimeError("Groq complaint classification failed after retry.")
