import discord
from discord.ext import commands
import asyncio
import random
import re

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.greetings = [
            "Здрасти, как си днес? 😊",
            "Хей, как върви денят ти? 😎",
            "Привет! Какво ново около теб? 🌟",
            "Хей, радвам се да те видя! 🤗",
            "Здравей! Как минава денят ти? ☀️",
        ]

    def is_bulgarian(self, text: str) -> bool:
        return bool(re.search(r"[А-Яа-я]", text))

    def translate_to_bg(self, text: str) -> str:
        response = self.bot.client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Преведи текста на естествен български език."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()

    @commands.command(name="питай", help="🤖 Задай въпрос на AI бота")
    async def chat(self, ctx, *, message: str):
        thinking_msg = await ctx.send("🤔 Мисля по въпроса...")

        try:
            loop = asyncio.get_event_loop()

            response = await loop.run_in_executor(
                None,
                lambda: self.bot.client_ai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Ти си весел Discord асистент. "
                                "Отговаряй винаги на български език, независимо на какъв език ти пишат. "
                                "Ако получиш чужд език – преведи и отговори на български. "
                                "Отговаряй приятелски, уверено и кратко. "
                                "Използвай различни приветствия, за да не звучиш еднообразно."
                            )
                        },
                        {"role": "user", "content": message}
                    ]
                )
            )

            reply = response.choices[0].message.content.strip()

            # Ако отговорът не е на кирилица → превеждаме
            if not self.is_bulgarian(reply):
                reply = self.translate_to_bg(reply)

            # Ако потребителят просто поздравява → дай случайно приветствие
            if message.lower() in ["здравей", "здрасти", "привет", "hello", "hi", "hey"]:
                reply = random.choice(self.greetings)

            await thinking_msg.edit(content=reply)

        except Exception as e:
            await thinking_msg.edit(content="⚠️ Възникна грешка при обработката на заявката.")
            print(f"[ChatCog] Error: {e}")

async def setup(bot):
    await bot.add_cog(ChatCog(bot))




































