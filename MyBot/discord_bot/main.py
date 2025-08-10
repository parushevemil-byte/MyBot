import discord
from discord.ext import commands
import os
import json
import logging
import asyncio
import sys
import re
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "bot_content.json")

config = {}
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Грешка в bot_content.json: {e}")

TOKEN = config.get("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN")
OPENAI_KEY = config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
PREFIX = config.get("PREFIX") or os.getenv("PREFIX") or "!"

if not TOKEN:
    print("❌ Липсва DISCORD_TOKEN!")
    sys.exit(1)
if not OPENAI_KEY:
    print("❌ Липсва OPENAI_API_KEY!")
    sys.exit(1)

client_ai = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(
    filename="bot_errors.log",
    level=logging.ERROR,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # ✅ Добавено за да работят статусите

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.client_ai = client_ai


def is_bulgarian(text: str) -> bool:
    return bool(re.search(r"[А-Яа-я]", text))


def translate_to_bg(text: str) -> str:
    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Преведи текста на естествен български език."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()


async def load_cogs():
    cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
    if not os.path.exists(cogs_path):
        print(f"⚠️ Папката {cogs_path} не съществува – пропускам cogs.")
        return

    for filename in os.listdir(cogs_path):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Зареден cog: {filename}")
            except Exception as e:
                print(f"❌ Грешка при зареждане на {filename}: {e}")


@bot.event
async def on_ready():
    print(f"🤖 Ботът е стартиран като {bot.user} | Префикс: {PREFIX}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if hasattr(message, "is_handled") and message.is_handled:
        return

    blocked_keywords = [
        "новини", "новото",
        "времето", "часът", "часа",
        "валута", "курс", "долар", "лев", "евро",
        "хороскоп", "зодия", "зодиите"
    ]

    lower_msg = message.content.lower()
    if any(word in lower_msg for word in blocked_keywords):
        return

    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Отговаряй винаги на български език."},
                {"role": "user", "content": message.content}
            ]
        )

        reply = response.choices[0].message.content.strip()
        if not is_bulgarian(reply):
            reply = translate_to_bg(reply)

        await message.channel.send(reply)

    except Exception as e:
        print(f"AI Error: {e}")
        await message.channel.send("⚠️ Възникна грешка при AI отговора.")


async def start_bot():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            print("⛔ Ботът е спрян ръчно.")
            break
        except Exception as e:
            print(f"⚠️ Грешка: {e}")
            print("🔄 Рестартиране след 5 секунди...")
            time.sleep(5)










































