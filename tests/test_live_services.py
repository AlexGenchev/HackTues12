"""
test_live_services.py
---------------------
This script tests the AI backend Python functions (via Groq API) directly using your 
.env configuration, without going through the FastAPI layer. This allows you to test 
various AI prompts rapidly without dealing with HTTP uploads or audio recordings.

Before running, make sure your .env has GROQ_API_KEY set.

Usage:
  python tests/test_live_services.py
"""

import sys
import os
import asyncio

# Ensure the backend module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from backend.services.transcription import transcribe_audio
from backend.services.classification import classify_complaint
from backend.services.formalization import formalize_complaint

# We use dummy text to avoid requiring live audio for this specific test
TEST_COMPLAINT_TEXT = (
    "Ало, вижте кво, тука на Цар Освободител в Своге има една дупка дето е кат кратер бе! "
    "Бахти смотаната работа, днеска двама комшии си пръснаха гумите вътре. "
    "Ае скачайте да го оправяте тва чудо бързо, че ми писна!"
)

async def main():
    print("Testing connection and .env variables...")
    load_dotenv()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        print("WARNING: GROQ_API_KEY is not set correctly in your .env file.")
        print("Please set it, otherwise the live AI tests will fail.\n")
    
    print("-" * 50)
    print("MOCK TRANSCRIPTION TEXT (Bypassing Audio Whisper File):")
    print(TEST_COMPLAINT_TEXT)
    print("-" * 50)
    
    print("\n[1/3] CLASSIFICATION SERVICE...")
    try:
        classification = await classify_complaint(TEST_COMPLAINT_TEXT)
        print("Classification Result:")
        print(f"  Category: {classification.get('category')}")
        print(f"  Urgency: {classification.get('urgency')}")
        print(f"  Location: {classification.get('location_mentioned')}")
    except Exception as e:
        print(f"\n[ERROR] Classification Failed: {e}")
        return

    print("\n[2/3] MUNICIPALITY LOOKUP...")
    from backend.data.municipalities import lookup_municipality
    from backend.data.department_emails import get_department_email
    
    loc = classification.get("location_mentioned")
    municipality_info = lookup_municipality(loc) if loc else None
    mun_name = municipality_info.get("municipality") if municipality_info else "Unknown"
    print(f"Resolved Municipality: {mun_name}")

    print("\n[3/3] FORMALIZATION SERVICE...")
    try:
        cat = classification.get("category", "OTHER")
        urg = classification.get("urgency", "MEDIUM")
        
        formal_letter = await formalize_complaint(
            text=TEST_COMPLAINT_TEXT,
            category=cat,
            location=loc,
            municipality=mun_name,
            urgency=urg
        )
        print("Formal Letter Output:")
        print("-" * 50)
        print(formal_letter)
        print("-" * 50)
    except Exception as e:
        print(f"\n[ERROR] Formalization Failed: {e}")
        return
        
    print("\nLive Services Test Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(main())
