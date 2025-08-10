import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import json
from datetime import datetime, timedelta
import re
import pytz

DATA_FILE = "reminders.json"
bg_tz = pytz.timezone("Europe/Sofia")

category_phrases = {
    "работа": ("💼", "е време да запретнеш ръкави и да работиш!"),
    "среща": ("📅", "не забравяй за важната си среща!"),
    "готвене": ("🍳", "хайде към кухнята – време е за вкусно готвене!"),
    "чистене": ("🧹", "нека домът заблести – време е за чистене!"),
    "разходка": ("🚶‍♂️", "излез и се наслади на свежия въздух!"),
    "пазар": ("🛍️", "трябва да отскочиш до магазина за пазаруване!"),
    "сън": ("😴", "време е за сладки сънища – лягай си!"),
    "събуждане": ("⏰", "събуди се – новият ден те очаква!"),
    "спорт": ("🏋️", "движението е здраве – време е за спорт!"),
    "лекарство": ("💊", "не забравяй да си вземеш лекарството!"),
    "любов": ("❤️", "покажи обич на любимите си хора!"),
    "забавление": ("🔥", "отпусни се – време е за забавление!"),
    "учене": ("📚", "разшири знанията си – време е за учене!"),
    "семейство": ("👨‍👩‍👧‍👦", "прекарай ценни мигове със семейството!"),
    "празник": ("🎉", "отбележи празника подобаващо!"),
    "финанси": ("💰", "време е да обърнеш внимание на финансите си!"),
    "пиене": ("🍻", "налей си нещо приятно за пиене!"),
    "музика": ("🎶", "пусни любимата си музика и се наслади!"),
    "пушене": ("🚬", "ако държиш – време е за почивка с цигара!"),
    "друго": ("🔔", "не забравяй каквото си планирал!")
}

def load_reminders():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_reminders(reminders):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

class CategoryView(View):
    def __init__(self, author, message):
        super().__init__(timeout=60)
        self.author = author
        self.message = message
        for emoji, label in [
            ("💼", "работа"), ("📅", "среща"), ("🍳", "готвене"),
            ("🧹", "чистене"), ("🚶‍♂️", "разходка"), ("🛍️", "пазар"),
            ("😴", "сън"), ("⏰", "събуждане"), ("🏋️", "спорт"),
            ("💊", "лекарство"), ("❤️", "любов"), ("🔥", "забавление"),
            ("📚", "учене"), ("👨‍👩‍👧‍👦", "семейство"), ("🎉", "празник"),
            ("💰", "финанси"), ("🍻", "пиене"), ("🎶", "музика"),
            ("🚬", "пушене"), ("🔔", "друго")
        ]:
            button = Button(label=label, emoji=emoji, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(label)
            self.add_item(button)

    async def on_timeout(self):
        try:
            await self.message.delete()
        except:
            pass

    def create_callback(self, label):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.author:
                await interaction.response.send_message("Това меню не е за теб!", ephemeral=True)
                return

            await interaction.message.delete()

            prompt_msg = await interaction.channel.send("**➡️ На кого да напомня? (посочи @потребител или напиши \"мен\")**")

            def check_user(m):
                return m.author == self.author and m.channel == interaction.channel

            user_msg = await interaction.client.wait_for("message", check=check_user)
            await user_msg.delete()
            await prompt_msg.delete()

            target_user = self.author.id
            if user_msg.mentions:
                target_user = user_msg.mentions[0].id

            time_prompt = await interaction.channel.send("**➡️ Въведи час във формат HH:MM (българско време):**")

            time_msg = await interaction.client.wait_for("message", check=check_user)

            try:
                hour, minute = map(int, time_msg.content.split(":"))
                now = datetime.now(bg_tz)
                remind_time = bg_tz.localize(datetime(now.year, now.month, now.day, hour, minute))
                if remind_time < now:
                    remind_time += timedelta(days=1)

                cog = interaction.client.get_cog("ReminderCog")
                if cog:
                    cog.reminders.append({
                        "time": remind_time.isoformat(),
                        "text": label,
                        "channel": interaction.channel.id,
                        "user": target_user,
                        "creator": self.author.id
                    })
                    save_reminders(cog.reminders)

            except:
                await interaction.channel.send("❌ Невалиден формат за час! Използвай HH:MM.")

            await time_msg.delete()
            await time_prompt.delete()

        return callback

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = load_reminders()
        self.reminder_checker.start()

    def cog_unload(self):
        self.reminder_checker.cancel()

    async def send_reminder(self, rem):
        channel = self.bot.get_channel(rem["channel"])
        if not channel:
            return

        emoji, phrase = category_phrases.get(rem["text"], ("🔔", f"не забравяй за {rem['text']}"))

        creator_mention = f"<@{rem['creator']}>"
        target_mention = f"<@{rem['user']}>"

        if rem["creator"] == rem["user"]:
            msg = f"{emoji} Хей {creator_mention}! Напомняне за теб: {phrase}"
        else:
            msg = f"{emoji} {creator_mention} ти напомня {target_mention}: {phrase}"

        await channel.send(msg)

    @tasks.loop(seconds=30)
    async def reminder_checker(self):
        now = datetime.now(bg_tz)
        to_remove = []

        for rem in self.reminders:
            remind_time = datetime.fromisoformat(rem["time"])
            if now >= remind_time:
                await self.send_reminder(rem)
                to_remove.append(rem)

        for rem in to_remove:
            self.reminders.remove(rem)
        if to_remove:
            save_reminders(self.reminders)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.strip().lower()
        if content.startswith("напомни ми") or content.startswith("напомни"):
            match = re.search(r"напомни (.+) в (\d{1,2}):(\d{2})", message.content, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                hour, minute = int(match.group(2)), int(match.group(3))
                now = datetime.now(bg_tz)
                remind_time = bg_tz.localize(datetime(now.year, now.month, now.day, hour, minute))
                if remind_time < now:
                    remind_time += timedelta(days=1)

                self.reminders.append({
                    "time": remind_time.isoformat(),
                    "text": text,
                    "channel": message.channel.id,
                    "user": message.author.id,
                    "creator": message.author.id
                })
                save_reminders(self.reminders)
                await message.reply(f"✅ Ще ти напомня за '{text}' в {hour:02d}:{minute:02d}.")
                return

            await message.delete()
            sent = await message.channel.send("**➡️ Избери категория, за която да получиш напомняне:**")
            view = CategoryView(message.author, sent)
            await sent.edit(view=view)

async def setup(bot):
    await bot.add_cog(ReminderCog(bot))



