import discord
from discord.ext import commands
import aiohttp
import asyncio
from deep_translator import GoogleTranslator

API_URL = "https://api.api-ninjas.com/v1/horoscope"
API_KEY = "YOUR_API_KEY"

ZODIAC_INFO = {
    "aries": ("♈", "овен"), "taurus": ("♉", "телец"), "gemini": ("♊", "близнаци"),
    "cancer": ("♋", "рак"), "leo": ("♌", "лъв"), "virgo": ("♍", "дева"),
    "libra": ("♎", "везни"), "scorpio": ("♏", "скорпион"), "sagittarius": ("♐", "стрелец"),
    "capricorn": ("♑", "козирог"), "aquarius": ("♒", "водолей"), "pisces": ("♓", "риби")
}

BG_TO_EN = {
    "овен": "aries", "телец": "taurus", "близнаци": "gemini", "рак": "cancer",
    "лъв": "leo", "лев": "leo", "дева": "virgo", "везни": "libra",
    "скорпион": "scorpio", "стрелец": "sagittarius", "козирог": "capricorn",
    "водолей": "aquarius", "риби": "pisces"
}

class HoroscopeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = GoogleTranslator(source='en', target='bg')

    async def get_horoscope(self, sign: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"zodiac": sign}, headers={"X-Api-Key": API_KEY}) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()

    async def send_horoscope(self, ctx, sign: str):
        sign_lower = sign.lower()
        if sign_lower in BG_TO_EN:
            sign_lower = BG_TO_EN[sign_lower]

        if sign_lower not in ZODIAC_INFO:
            await ctx.send("❗ Невалидна зодия. Пример: овен, телец, лъв, риби...")
            return

        data = await self.get_horoscope(sign_lower)
        if not data:
            await ctx.send("⚠️ Грешка при извличане на хороскопа.")
            return

        text_en = data.get("horoscope", "")
        text_bg = await asyncio.get_event_loop().run_in_executor(None, self.translator.translate, text_en)

        emoji, bg_name = ZODIAC_INFO[sign_lower]

        embed = discord.Embed(
            title=f"{emoji} Хороскоп за {bg_name}",
            description=text_bg,
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Дата: {data.get('date', '')}")
        await ctx.send(embed=embed)

    @commands.command(name="дневенхороскоп")
    async def horoscope_cmd(self, ctx, sign: str):
        await self.send_horoscope(ctx, sign)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.strip().lower()
        if content.startswith("хороскоп за"):
            parts = content.split()
            if len(parts) >= 3:
                sign = parts[2]
                ctx = await self.bot.get_context(message)
                await self.send_horoscope(ctx, sign)

async def setup(bot):
    await bot.add_cog(HoroscopeCog(bot))

