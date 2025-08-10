import discord
from discord.ext import commands
import random

class LegendNotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1313162310130339891  # <-- Сложи ID на канала
        self.target_id = 1036929405085290556   # <-- Сложи ID на човека

        self.messages = [
            "⚔️ Diablo II Легендата {mention} се завърна сред нас – героите я приветстват!",
            "🔥 Вратите на ада се затварят – Diablo II Легендата {mention} е онлайн!",
            "💀 Diablo II Легендата {mention} пристигна – демоните отстъпват в паника!",
            "🗡 Sanctuary сияе – Diablo II Легендата {mention} е отново тук!",
            "🏆 Един велик момент – Diablo II Легендата {mention} е онлайн!",
            "⚡ Diablo II Легендата {mention} се появи – силата ѝ озарява света!",
            "🐉 Diablo II Легендата {mention} пристигна – злото няма къде да се скрие!",
            "🔮 Diablo II Легендата {mention} е тук – магията на древните сили оживява!",
            "🧙‍♂️ Sanctuary ликува – Diablo II Легендата {mention} е отново сред героите!",
            "🗡 Великият миг настъпи – Diablo II Легендата {mention} се завърна онлайн!",
            "🔥 Огньовете на ада пламват – Diablo II Легендата {mention} е в играта!",
            "⚔️ Легендата {mention} се пробужда – враговете треперят!",
            "🏹 Diablo II Легендата {mention} се появи – стрелите на съдбата са готови!",
            "🛡 Чуйте звука на славата – Diablo II Легендата {mention} е на линия!",
            "⚡ Всички демони бягат – Diablo II Легендата {mention} пристигна!",
            "🔥 Святата земя отново има своя герой – Diablo II Легендата {mention} е тук!",
            "💀 Героите на Sanctuary викат името {mention} – Легендата е онлайн!",
            "🗡 Всички търговци потриват ръце – Diablo II Легендата {mention} е пристигнала!",
            "⚔️ Злото се крие – Diablo II Легендата {mention} се появи на хоризонта!",
            "🏆 Поредният велик ден – Diablo II Легендата {mention} е тук!",
            "🔮 Всички рунни думи трептят – Diablo II Легендата {mention} е онлайн!",
            "🛡 Легендата {mention} е отново в Sanctuary – съюзниците ликуват!",
            "⚡ Силата на древните герои оживява – Diablo II Легендата {mention} е на линия!",
            "🐉 Героите потръпват – Diablo II Легендата {mention} се завърна!",
            "🔥 Всички пътища водят към славата – Diablo II Легендата {mention} е онлайн!",
            "🏹 Оръжията са готови – Diablo II Легендата {mention} е сред нас!",
            "💀 Демоните се разбягват – Diablo II Легендата {mention} е тук!",
            "⚔️ Нови приключения предстоят – Diablo II Легендата {mention} се появи!",
            "🗡 Отново ще има битки – Diablo II Легендата {mention} се завърна!",
            "🏆 Sanctuary приветства героя – Diablo II Легендата {mention} е онлайн!"
        ]

        self.last_status = None  # ще пазим последния статус

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.id != self.target_id:
            return  # интересува ни само конкретният човек

        current_status = str(after.status)

        if current_status == "offline":
            self.last_status = "offline"
            return

        # Ако преди е бил offline, а сега вече е online/idle/dnd
        if self.last_status == "offline":
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                msg = random.choice(self.messages).format(mention=after.mention)
                await channel.send(msg)

        self.last_status = current_status

async def setup(bot):
    await bot.add_cog(LegendNotify(bot))

