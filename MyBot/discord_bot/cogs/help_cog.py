import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=60)

        # 📰 Информация
        self.add_item(Button(label="📰 Новини", style=discord.ButtonStyle.primary, custom_id="news"))
        self.add_item(Button(label="🌦️ Времето", style=discord.ButtonStyle.primary, custom_id="weather"))
        self.add_item(Button(label="🔮 Хороскоп", style=discord.ButtonStyle.primary, custom_id="horoscope"))
        self.add_item(Button(label="💱 Валута", style=discord.ButtonStyle.primary, custom_id="currency"))

        # ⏰ Време и напомняния
        self.add_item(Button(label="⏰ Напомняне", style=discord.ButtonStyle.success, custom_id="reminder"))
        self.add_item(Button(label="🕒 Час", style=discord.ButtonStyle.success, custom_id="time"))

        # 📜 Всички команди
        self.add_item(Button(label="📜 Всички команди", style=discord.ButtonStyle.secondary, custom_id="all"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        commands_text = {
            "news": "Пример: **!новини**",
            "weather": "Пример: **!времето София**",
            "horoscope": "Пример: **!хороскоп за лъв**",
            "currency": "Пример: **!валута USD**",
            "reminder": "Пример: **Напомни ми да спортувам в 18:00**",
            "time": "Пример: **!час**",
            "all": (
                "📜 **Всички команди:**\n"
                "📰 Новини → `!новини`\n"
                "🌦️ Времето → `!времето София`\n"
                "🔮 Хороскоп → `!хороскоп за лъв`\n"
                "💱 Валута → `!валута USD`\n"
                "⏰ Напомняне → `Напомни ми да спортувам в 18:00`\n"
                "🕒 Час → `!час`"
            )
        }

        cid = interaction.data["custom_id"]
        if cid in commands_text:
            await interaction.response.send_message(commands_text[cid], ephemeral=True)
            await interaction.message.delete()  # изтриваме менюто

            # След 60 секунди трием ephemeral съобщението
            await asyncio.sleep(60)
            try:
                await interaction.delete_original_response()
            except discord.NotFound:
                pass

        return True


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_help_menu(self, channel: discord.TextChannel):
        embed = discord.Embed(
            title="📌 Помощно меню",
            description="Избери една от опциите по-долу, за да видиш пример за команда.",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=HelpView())

    @commands.command(name="помощ")
    async def help_command(self, ctx: commands.Context):
        await self.send_help_menu(ctx.channel)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.content.strip().lower() == "помощ":
            await self.send_help_menu(message.channel)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))








