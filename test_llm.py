import os
import requests
from datetime import date

OLLAMA = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"  # try "qwen2.5:7b" for better accuracy

# Replicate the user's prompt here:
USER_QUERY = "How much did I spend on groceries in the last 3 months?"

menu_path = os.path.join(os.path.dirname(__file__), "menu.txt")
system_prompt = open(menu_path).read()

payload = {
    "model": MODEL,
    "format": "json",  # force valid JSON output
    "stream": False,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"CURRENT_DATE: {date.today().isoformat()}\n\nQ: {USER_QUERY}"},
    ],
}

r = requests.post(OLLAMA, json=payload)
r.raise_for_status()
print(r.json()["message"]["content"])

'''
pick here:
1. test_llm.py aur menu.txt ko server pe dalo
2. USER_QUERY update karke response dekho
3. agar response galat ata hai, download qwen2.5:7b
4. wo 3 ke alawa, ek naya use-case socha. iska test karo, kya response ata hai?
5. update ask.py (a/test_llm.py)'''
