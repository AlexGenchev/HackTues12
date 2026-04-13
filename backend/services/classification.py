import json, os
from groq import AsyncGroq

async def classify_complaint(text: str) -> dict:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    res = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Ти си система за класифициране на жалби. Върни само JSON."},
            {"role": "user", "content": f"""Анализирай и върни JSON: 
- "category": (WATER_SUPPLY, ELECTRICITY, ROADS, WASTE_MANAGEMENT, PUBLIC_ORDER, GREEN_SPACES, ADMINISTRATIVE, OTHER)
- "location_mentioned": град/село (string) или null
- "urgency": "HIGH", "MEDIUM" или "LOW"
ЖАЛБА: {text}"""}
        ],
        temperature=0.1, max_tokens=256
    )
    raw = res.choices[0].message.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)
    return {
        "category": data.get("category", "OTHER").upper(),
        "location_mentioned": str(data["location_mentioned"]).strip().lower() if data.get("location_mentioned") else None,
        "urgency": data.get("urgency", "MEDIUM").upper()
    }

