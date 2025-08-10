import discord
from discord.ext import commands
import pytz
from datetime import datetime

class TimeChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_city_time(self, city):
        timezones = {
            "токио": "Asia/Tokyo",
            "лондон": "Europe/London",
            "ню йорк": "America/New_York",
            "аляска": "America/Anchorage",
            "софия": "Europe/Sofia",
        }
        city_lower = city.lower()
        if city_lower not in timezones:
            return None

        tz = pytz.timezone(timezones[city_lower])
        now = datetime.now(tz)
        return now.strftime("%H:%M, %d %B %Y")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        text = message.content.lower()

        if any(word in text for word in ["колко е часът", "часът", "времето", "часа"]):
            cities = ["токио", "лондон", "ню йорк", "аляска", "софия"]
            found_city = None
            for city in cities:
                if city in text:
                    found_city = city
                    break

            if found_city:
                city_time = await self.get_city_time(found_city)
                if city_time:
                    await message.channel.send(f"⏰ В **{found_city.title()}** е {city_time}.")
                else:
                    await message.channel.send("❌ Не мога да намеря часа за това място.")

async def setup(bot):
    await bot.add_cog(TimeChat(bot))



