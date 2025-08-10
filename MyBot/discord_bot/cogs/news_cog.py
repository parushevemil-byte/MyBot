import discord
from discord.ext import commands, tasks
import feedparser
from datetime import datetime
import pytz
import re
import time

NEWS_FEEDS = [
    "https://www.dnevnik.bg/rss/",
    "https://www.24chasa.bg/rss",
    "https://www.mediapool.bg/rss/",
    "https://www.dir.bg/rss"
]

TIMEZONE = pytz.timezone("Europe/Sofia")
last_news_time = 0  # предотвратяване на спам

def get_all_news(limit=3):
    all_news = []

    for url in NEWS_FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            all_news.append({
                "title": entry.title,
                "link": entry.link,
                "source": url.split("//")[1].split("/")[0]
            })

    return all_news[:limit]

class NewsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_news.start()

    def cog_unload(self):
        self.send_news.cancel()

    async def send_news_embed(self, channel):
        news_items = get_all_news(limit=3)
        if not news_items:
            await channel.send("❌ Няма налични новини.")
            return

        embed = discord.Embed(
            title="📰 Най-важното днес",
            color=discord.Color.blue()
        )

        for news in news_items:
            embed.add_field(
                name=f"🔹 {news['title']}",
                value=f"[🔗 Прочети повече]({news['link']}) ({news['source']})",
                inline=False
            )

        embed.set_footer(
            text="Източници: Dnevnik, 24 Часа, Mediapool, Dir.bg • " +
            datetime.now(TIMEZONE).strftime("%H:%M")
        )
        await channel.send(embed=embed)

    # ✅ Команда за новини
    @commands.command(name="новини")
    async def cmd_news(self, ctx):
        await self.send_news_embed(ctx.channel)

    # ✅ Автоматично изпращане по график (8:00, 12:00, 19:00)
    @tasks.loop(minutes=1)
    async def send_news(self):
        now = datetime.now(TIMEZONE)
        if now.minute == 0 and now.hour in [8, 12, 19]:
            if hasattr(self.bot, "news_channel_id"):
                channel = self.bot.get_channel(int(self.bot.news_channel_id))
                if channel:
                    await self.send_news_embed(channel)

    @send_news.before_loop
    async def before_send_news(self):
        await self.bot.wait_until_ready()

    # ✅ Автоматичен отговор на въпроси
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        global last_news_time

        if message.author.bot:
            return

        if re.search(r"(какви са|има ли|кажи|покажи).*(новини|актуалното|новото)", message.content, re.IGNORECASE):
            now = time.time()
            if now - last_news_time < 10:
                return  # предотвратява спам

            last_news_time = now
            await self.send_news_embed(message.channel)
            message.is_handled = True

async def setup(bot):
    await bot.add_cog(NewsCog(bot))















