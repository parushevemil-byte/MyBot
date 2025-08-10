import os
import json
import openai

# Абсолютен път към bot_content.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "bot_content.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

OPENAI_API_KEY = config.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def get_openai_response(prompt: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ Грешка при заявката към OpenAI: {e}"


