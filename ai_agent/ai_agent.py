import google.generativeai as genai
import json
import sys

# Оправя кирилицата
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ТВОЯТ КЛЮЧ
genai.configure(api_key="AIzaSyAxAjx4I6TT33as56j4OpDAGoX7DdDPR2I")

# ТУК Е ПРОМЯНАТА: Добавяме пълното име и транспортен протокол
model = genai.GenerativeModel(
    model_name='models/gemini-1.5-flash'
)

def viK_agent_process(user_speech_text):
    prompt = f"""
    Ти си администратор във ВиК. Извлечи JSON:
    1. 'Владо Тричков' -> район 'Своге'.
    2. 'issue_type': 'Нарушено водоснабдяване' или 'Друг проблем'.
    
    Върни САМО JSON:
    {{
        "region": "район",
        "village": "село",
        "address": "адрес",
        "issue_type": "проблем"
    }}
    Текст: "{user_speech_text}"
    """
    
    try:
        # Използваме директно генериране
        response = model.generate_content(prompt)
        
        if not response.text:
            return {"error": "Empty response from AI"}
            
        clean_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_text)
    except Exception as e:
        return {"error": "AI Error", "details": str(e)}

# ТЕСТ
test_text = "Има авария във Владо Тричков на улица Витоша 5"
result = viK_agent_process(test_text)

print("\n--- РЕЗУЛТАТ ОТ АГЕНТА ---")
print(json.dumps(result, indent=4, ensure_ascii=False))