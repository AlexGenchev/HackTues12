import json, os, asyncio, time
from groq import AsyncGroq
from playwright.sync_api import sync_playwright

# ViK Sofia coverage - village key → municipality name for the form dropdown
_LOCATIONS = {
    "божурище": "Божурище", "гурмазово": "Божурище", "златуша": "Божурище",
    "ботевград": "Ботевград", "врачеш": "Ботевград",
    "годеч": "Годеч",
    "горна малина": "Горна Малина",
    "долна баня": "Долна Баня",
    "драгоман": "Драгоман",
    "елин пелин": "Елин Пелин",
    "ихтиман": "Ихтиман",
    "костенец": "Костенец",
    "костинброд": "Костинброд",
    "своге": "Своге", "бакьово": "Своге", "батулия": "Своге", "бов": "Своге",
    "брезе": "Своге", "буковец": "Своге", "владо тричков": "Своге",
    "габровница": "Своге", "гара бов": "Своге", "гара лакатник": "Своге",
    "губислав": "Своге", "добравица": "Своге", "дружево": "Своге",
    "сливница": "Сливница", "алдомировци": "Сливница", "братушково": "Сливница",
    "гургулят": "Сливница", "ракита": "Сливница",
}


def _wait_and_select(page, select_id: str, label_text: str, timeout: int = 10000):
    locator = page.locator(f"#{select_id}")
    locator.wait_for(state="visible", timeout=timeout)
    for _ in range(20):
        if locator.locator("option").count() > 1:
            break
        time.sleep(0.3)
    for opt in locator.locator("option").all():
        text = opt.inner_text().strip()
        if label_text.lower() in text.lower():
            locator.select_option(value=opt.get_attribute("value"))
            return
    available = [o.inner_text().strip() for o in locator.locator("option").all()]
    raise ValueError(f"Option '{label_text}' not found in #{select_id}. Available: {available}")


def _submit_vik_form_sync(name: str, village: str, address: str, municipality: str, description: str):
    contact_email = os.getenv("VIK_CONTACT_EMAIL", "bojidarmarkov3.0@gmail.com")
    contact_phone = os.getenv("VIK_CONTACT_PHONE", "0882482180")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto("https://viksofbg.com/signal/")
            page.wait_for_load_state("networkidle")

            # dismiss survey popup if present
            try:
                page.wait_for_selector("#hustle-popup-id-1", timeout=5000)
                page.evaluate("document.querySelector('#hustle-popup-id-1').remove()")
            except Exception:
                pass

            page.locator("#vik-signal-name").fill(name)
            page.locator("#vik-signal-email").fill(contact_email)
            page.locator("#vik-signal-phone").fill(contact_phone)

            _wait_and_select(page, "vik-signal-region", municipality)
            time.sleep(2)  # wait for settlement dropdown to populate
            _wait_and_select(page, "vik-signal-settlement", village)

            page.locator("#vik-signal-address").fill(address)

            radio = page.locator("input[name='vik-signal-reason-radio'][value='other']")
            radio.wait_for(state="attached", timeout=5000)
            radio.check()

            time.sleep(0.5)
            page.locator("#vik-signal-description").wait_for(state="visible", timeout=5000)
            page.locator("#vik-signal-description").fill(description)
        finally:
            browser.close()


async def fill_vik_form(transcribed_text: str) -> bool:
    """Extract structured data from voice text via LLM then fill the ViK Sofia web form."""
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""Ти си администратор във ВиК. Превърни текста в официален сигнал.
Върни САМО валиден JSON без никакъв друг текст:
{{
    "name": "ime na podatelia ili 'Анонимен' ako nqma",
    "village": "точно ime na seloto s 's.' otpred, napr. 'с. Владо Тричков'",
    "address": "toch adres ili 'Неизвестен' ako nqma",
    "official_description": "Profesionalno napisano oplakване na balgarski ezik"
}}
Текст: "{transcribed_text}"
"""
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500,
    )
    raw = response.choices[0].message.content.strip()
    ai_data = json.loads(raw.replace("```json", "").replace("```", "").strip())

    village_key = ai_data["village"].lower().replace("с. ", "").strip()
    municipality = _LOCATIONS.get(village_key, "Своге")

    await asyncio.to_thread(
        _submit_vik_form_sync,
        ai_data["name"],
        ai_data["village"],
        ai_data["address"],
        municipality,
        ai_data["official_description"],
    )
    return True
