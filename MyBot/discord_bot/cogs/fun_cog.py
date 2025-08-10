import random
import discord
from discord.ext import commands

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Може да се чете от JSON файл в бъдеще
        self.content = {
            "facts": [
                "🌍 Земята е третата планета от Слънцето.",
                "💧 Водата покрива 71% от Земята.",
                "🚀 Първият човек в Космоса е Юрий Гагарин (1961 г.).",
                "🐝 Пчелите могат да разпознават човешки лица!"
            ],
            "daily_tips": [
                "💦 Пий повече вода днес!",
                "🏃 Излез на кратка разходка – движението е здраве!",
                "📚 Научи нещо ново – мозъкът също има нужда от тренировка.",
                "😊 Усмихни се на някого – добротата е заразна!"
            ],
            "wise_thoughts": [
                "🌟 „Животът е като огледало – усмихни му се и той ще ти отвърне.“",
                "🌱 „Всяко голямо пътешествие започва с малка стъпка.“",
                "🔥 „Не чакай перфектния момент – създай го!“",
                "💡 „Знанието е сила, но мъдростта е свобода.“"
            ],
            "horoscopes": [
                "✨ Днес е ден за нови идеи и приятни срещи!",
                "🌞 Очаква те позитивна изненада – приеми я с усмивка!",
                "🍀 Днес късметът е на твоя страна!",
                "❤️ Ще получиш топли думи от близък човек.",
                "💪 Денят е подходящ за действие – не отлагай!"
            ]
        }

    def create_embed(self, title, description, color=discord.Color.random()):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="🤖 Създадено от твоя Discord бот")
        return embed

    @commands.command(name="факт", help="📚 Получи случаен интересен факт.")
    async def факт(self, ctx):
        facts = self.content["facts"]
        embed = self.create_embed("📚 Случаен факт", random.choice(facts))
        await ctx.send(embed=embed)

    @commands.command(name="съвет", help="📝 Получи полезен ежедневен съвет.")
    async def съвет(self, ctx):
        tips = self.content["daily_tips"]
        embed = self.create_embed("📝 Днешен съвет", random.choice(tips))
        await ctx.send(embed=embed)

    @commands.command(name="мисъл", help="💭 Получи мъдра мисъл за деня.")
    async def мисъл(self, ctx):
        thoughts = self.content["wise_thoughts"]
        embed = self.create_embed("💭 Мъдра мисъл", random.choice(thoughts))
        await ctx.send(embed=embed)

    @commands.command(name="хороскоп", help="🔮 Получи дневен хороскоп за твоята зодия.")
    async def хороскоп(self, ctx, *, знак: str = None):
        if not знак:
            await ctx.send("❗ Моля, въведи зодия след командата. Пример: `!хороскоп овен`")
            return
        horoscope = random.choice(self.content["horoscopes"])
        embed = self.create_embed(f"🔮 Хороскоп за {знак.capitalize()}", horoscope)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FunCog(bot))

