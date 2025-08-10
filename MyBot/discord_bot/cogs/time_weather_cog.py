import discord
from discord.ext import commands
import aiohttp
from datetime import datetime
import pytz
import os
import re

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

class TimeWeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_weather(self, city):
        if not OPENWEATHER_KEY:
            return None

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=bg"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()

    async def build_weather_embed(self, city):
        data = await self.get_weather(city)
        if not data or data.get("cod") != 200:
            return None

        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        embed = discord.Embed(
            title=f"🌤 Времето в {city.title()}",
            description=f"{weather_desc}, {temp}°C (усеща се като {feels_like}°C)",
            color=0x2ECC71
        )
        embed.add_field(name="💧 Влажност", value=f"{humidity}%", inline=True)
        embed.add_field(name="💨 Вятър", value=f"{wind_speed} m/s", inline=True)
        embed.set_footer(text="Данни от OpenWeather")

        return embed

    async def get_time_for_city(self, city):
        tz_map = {
            "софия": "Europe/Sofia",
            "пловдив": "Europe/Sofia",
            "варна": "Europe/Sofia",
            "бургас": "Europe/Sofia",
            "лондон": "Europe/London",
            "ню йорк": "America/New_York",
            "лос анджелис": "America/Los_Angeles",
            "париж": "Europe/Paris",
            "берлин": "Europe/Berlin",
        }

        tz = tz_map.get(city.lower())
        if not tz:
            return None

        now = datetime.now(pytz.timezone(tz))
        return now.strftime("%H:%M, %d.%m.%Y")

    # ✅ Команда за времето
    @commands.command(name="времето")
    async def cmd_weather(self, ctx, *, city: str):
        embed = await self.build_weather_embed(city)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ Не успях да намеря времето за този град.")

    # ✅ Команда за часа
    @commands.command(name="час")
    async def cmd_time(self, ctx, *, city: str):
        time_str = await self.get_time_for_city(city)
        if time_str:
            await ctx.send(f"⏰ В **{city.title()}** е {time_str}.")
        else:
            await ctx.send("⚠️ Не успях да намеря времето за този град.")

    # ✅ Автоматичен отговор при въпрос
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        weather_match = re.search(r"(?:времето|какво е времето).*в\s+([А-Яа-яA-Za-z\s\-]+)", message.content, re.IGNORECASE)
        time_match = re.search(r"(?:часът|колко е часът).*в\s+([А-Яа-яA-Za-z\s\-]+)", message.content, re.IGNORECASE)

        if weather_match:
            city = weather_match.group(1).strip()
            embed = await self.build_weather_embed(city)
            if embed:
                await message.channel.send(embed=embed)
                message.is_handled = True
            return

        if time_match:
            city = time_match.group(1).strip()
            time_str = await self.get_time_for_city(city)
            if time_str:
                await message.channel.send(f"⏰ В **{city.title()}** е {time_str}.")
                message.is_handled = True
            return

async def setup(bot):
    await bot.add_cog(TimeWeatherCog(bot))



































