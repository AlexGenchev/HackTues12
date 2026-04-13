import os
from datetime import date
from typing import Optional
from groq import AsyncGroq

async def formalize_complaint(text: str, category: str, location: Optional[str], municipality: Optional[str], urgency: str) -> str:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    res = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Ти си административен асистент. Преформулирай гражданската жалба в официален стил на български."},
            {"role": "user", "content": f"""ДО: Общинска администрация\nОБЩИНА: {municipality or 'Общината'}\nОТНОСНО: Сигнал - {category}\n\nПисмо от гражданин на {location or 'общината'}.\nДата: {date.today().strftime('%d.%m.%Y')}\nОРИГИНАЛ: {text}\nВърни само текста на писмото."""}
        ],
        temperature=0.3, max_tokens=1024
    )
    return res.choices[0].message.content.strip()
