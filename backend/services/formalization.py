# backend/services/formalization.py
# Rewrites a raw citizen complaint into a formal Bulgarian administrative
# letter using the Groq LLM API.

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Optional

from groq import Groq

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)
_RETRY_WAIT_SECONDS = 2

_SYSTEM_PROMPT = (
    "Ти си административен асистент. Преформулирай гражданската жалба в "
    "официален административен стил на български език. Запази всички факти. "
    "Не добавяй измислена информация."
)

# Maps internal category codes to human-readable Bulgarian department names.
_CATEGORY_DEPARTMENTS: dict[str, str] = {
    "WATER_SUPPLY":    "Отдел Водоснабдяване и канализация",
    "ELECTRICITY":     "Отдел Електроснабдяване и улично осветление",
    "ROADS":           "Отдел Пътна инфраструктура и транспорт",
    "WASTE_MANAGEMENT":"Отдел Управление на отпадъците",
    "PUBLIC_ORDER":    "Отдел Обществен ред и сигурност",
    "GREEN_SPACES":    "Отдел Зелена система и паркове",
    "ADMINISTRATIVE":  "Отдел Административно обслужване",
    "OTHER":           "Общинска администрация",
}

# Maps category codes to Bulgarian topic strings used in ОТНОСНО header.
_CATEGORY_BG: dict[str, str] = {
    "WATER_SUPPLY":    "водоснабдяване",
    "ELECTRICITY":     "електроснабдяване",
    "ROADS":           "пътна инфраструктура",
    "WASTE_MANAGEMENT":"управление на отпадъците",
    "PUBLIC_ORDER":    "обществен ред",
    "GREEN_SPACES":    "зелени площи",
    "ADMINISTRATIVE":  "административни въпроси",
    "OTHER":           "граждански сигнал",
}

_USER_PROMPT_TEMPLATE = """Преформулирай следната гражданска жалба в официално административно писмо на български език.

Категория на проблема: {category_bg}
Населено място: {location}
Приоритет: {urgency_bg}
Изпращач на писмото: Гражданин на {location}

Структурирай писмото ТОЧНО по следния шаблон (запълни [...]):

ДО: {department}
ОБЩИНА: {municipality}

ОТНОСНО: Сигнал за {category_bg}

УВАЖАЕМИ ДАМИ И ГОСПОДА,

[2-3 официални параграфа на официален административен български, запазвайки ВСИЧКИ факти от оригиналния текст. Не измисляй нова информация.]

С уважение,
Гражданин на {location}
Дата: {date_bg}

ОРИГИНАЛЕН ТЕКСТ НА ЖАЛБАТА:
{transcribed_text}

Върни САМО текста на писмото без никакви допълнителни обяснения."""

_URGENCY_BG = {"HIGH": "ВИСОК", "MEDIUM": "СРЕДЕН", "LOW": "НИСkИ"}


def _bulgarian_date(d: date) -> str:
    """Format a date as DD.MM.YYYY (Bulgarian administrative convention)."""
    return d.strftime("%d.%m.%Y")


def _formalize_sync(
    transcribed_text: str,
    category: str,
    location: str,
    municipality: str,
    urgency: str,
    client: Groq,
) -> str:
    """Blocking LLM call to produce the formal letter — runs in thread pool."""
    department = _CATEGORY_DEPARTMENTS.get(category, "Общинска администрация")
    category_bg = _CATEGORY_BG.get(category, "граждански сигнал")
    urgency_bg = _URGENCY_BG.get(urgency, "СРЕДЕН")
    date_bg = _bulgarian_date(date.today())

    prompt = _USER_PROMPT_TEMPLATE.format(
        department=department,
        municipality=municipality,
        category_bg=category_bg,
        location=location,
        urgency_bg=urgency_bg,
        date_bg=date_bg,
        transcribed_text=transcribed_text,
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


async def formalize_complaint(
    transcribed_text: str,
    category: str,
    location: Optional[str],
    municipality: Optional[str],
    urgency: str,
) -> str:
    """Rewrite a raw Bulgarian complaint as a formal administrative letter.

    location and municipality may be None; safe defaults are used in that case.
    Retries once after 2 seconds on failure before raising.
    Raises RuntimeError if formalization fails after retry.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    loop = asyncio.get_event_loop()

    safe_location = location or "общината"
    safe_municipality = municipality or "Общината"

    for attempt in range(2):
        try:
            logger.info("Formalization attempt %d.", attempt + 1)
            letter = await loop.run_in_executor(
                _executor,
                _formalize_sync,
                transcribed_text,
                category,
                safe_location,
                safe_municipality,
                urgency,
                client,
            )
            logger.info("Formalization succeeded (%d chars).", len(letter))
            return letter
        except Exception as exc:
            logger.error("Formalization attempt %d failed: %s", attempt + 1, exc)
            if attempt == 0:
                await asyncio.sleep(_RETRY_WAIT_SECONDS)

    raise RuntimeError("Groq complaint formalization failed after retry.")
