import discord
from discord.ext import commands, tasks
import requests
import xml.etree.ElementTree as ET
import traceback
from datetime import datetime
import re

BNB_URL = "https://www.bnb.bg/Statistics/StExternalSector/StExchangeRates/StERForeignCurrencies/?download=xml&lang=EN"

class CurrencyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.exchange_data = {}
        self.current_date = ""

        self.currency_names = {
            "USD": ("Долар", "🇺🇸"),
            "EUR": ("Евро", "🇪🇺"),
            "BGN": ("Лев", "🇧🇬"),
            "GBP": ("Паунд", "🇬🇧"),
            "CHF": ("Франк", "🇨🇭"),
            "JPY": ("Йена", "🇯🇵"),
            "CNY": ("Юан", "🇨🇳"),
            "RUB": ("Рубла", "🇷🇺"),
            "CAD": ("Канадски долар", "🇨🇦"),
            "AUD": ("Австралийски долар", "🇦🇺"),
            "NOK": ("Норвежка крона", "🇳🇴"),
            "SEK": ("Шведска крона", "🇸🇪"),
            "PLN": ("Злота", "🇵🇱"),
            "TRY": ("Турска лира", "🇹🇷"),
            "INR": ("Рупия", "🇮🇳"),
            "BRL": ("Реал", "🇧🇷"),
            "MXN": ("Песо", "🇲🇽"),
            "ZAR": ("Ранд", "🇿🇦"),
            "SGD": ("Сингапурски долар", "🇸🇬"),
            "HKD": ("Хонконгски долар", "🇭🇰"),
            "NZD": ("Новозеландски долар", "🇳🇿"),
        }

        # ✅ Единствено и множествено число
        self.currency_map = {
            "долар": "USD", "долара": "USD", "долари": "USD",
            "евро": "EUR", "евра": "EUR",
            "лев": "BGN", "лева": "BGN", "левове": "BGN",
            "паунд": "GBP", "паунда": "GBP", "паунди": "GBP",
            "франк": "CHF", "франка": "CHF", "франкове": "CHF",
            "йена": "JPY", "йени": "JPY",
            "юан": "CNY", "юана": "CNY", "юани": "CNY",
            "рубла": "RUB", "рубли": "RUB",
            "лира": "TRY", "лири": "TRY",
            "рупия": "INR", "рупии": "INR",
            "реал": "BRL", "реала": "BRL", "реали": "BRL",
            "злота": "PLN", "злоти": "PLN",
            "песо": "MXN", "песота": "MXN", "песос": "MXN",
            "ранд": "ZAR", "ранда": "ZAR", "рандове": "ZAR",
            "крона": "NOK", "крони": "NOK",
            "шведска крона": "SEK", "шведски крони": "SEK",
            "канадски долар": "CAD", "канадски долара": "CAD", "канадски долари": "CAD",
            "австралийски долар": "AUD", "австралийски долара": "AUD", "австралийски долари": "AUD",
            "сингапурски долар": "SGD", "сингапурски долара": "SGD", "сингапурски долари": "SGD",
            "хонконгски долар": "HKD", "хонконгски долара": "HKD", "хонконгски долари": "HKD",
            "новозеландски долар": "NZD", "новозеландски долара": "NZD", "новозеландски долари": "NZD",
        }

        self.update_rates.start()

    def fetch_bnb_data(self):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(BNB_URL, headers=headers, timeout=10)
            if response.status_code != 200 or len(response.content) < 200:
                return False

            root = ET.fromstring(response.content)
            new_data = {}

            for record in root.findall("ROW"):
                code_elem = record.find("CODE")
                rate_elem = record.find("RATE")
                ratio_elem = record.find("RATIO")

                if code_elem is None or rate_elem is None or ratio_elem is None:
                    continue

                code = code_elem.text.strip() if code_elem.text else ""
                rate_text = rate_elem.text.strip() if rate_elem.text else ""
                ratio_text = ratio_elem.text.strip() if ratio_elem.text else ""

                try:
                    rate = float(rate_text.replace(",", "."))
                    ratio = float(ratio_text.replace(",", "."))
                except ValueError:
                    continue

                new_data[code] = rate / ratio

            new_data["BGN"] = 1.0

            days_elem = root.find("HEADER/DAYS")
            self.current_date = days_elem.text.strip() if days_elem is not None and days_elem.text else ""
            self.exchange_data = new_data
            return True

        except:
            traceback.print_exc()
            return False

    # ✅ Поправена формула
    def get_rate_priority(self, base, target):
        if base in self.exchange_data and target in self.exchange_data:
            rate = self.exchange_data[base] / self.exchange_data[target]
            reverse_rate = 1 / rate
            return rate, reverse_rate
        return None

    @tasks.loop(hours=6)
    async def update_rates(self):
        self.fetch_bnb_data()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.exchange_data:
            self.fetch_bnb_data()

    def format_currency(self, code: str):
        name, flag = self.currency_names.get(code, (code, ""))
        return f"{flag} {name}"

    async def send_rate(self, channel, base, target, amount=None):
        result = self.get_rate_priority(base, target)
        today = datetime.now().strftime("%d.%m.%Y")

        if not result:
            msg = f"❌ Няма налични данни за тези валути ({today})"
        else:
            rate, reverse_rate = result
            base_str = self.format_currency(base)
            target_str = self.format_currency(target)

            msg = (
                f"💱 {f'{amount:,.2f} ' if amount else ''}{base_str} → {target_str} ({today})\n"
                f"1 {base_str} = {rate:.4f} {target_str}\n"
                f"↩ 1 {target_str} = {reverse_rate:.4f} {base_str}"
            )

            if amount:
                total = rate * amount
                msg += f"\n💰 {amount:,.2f} {base_str} = {total:,.2f} {target_str}"

        await channel.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        text = message.content.lower()
        if not any(word in text for word in ["курс", "колко", "какъв е"]):
            return

        amount_match = re.search(r"(\d+[.,]?\d*)", text)
        amount = float(amount_match.group(1).replace(",", "")) if amount_match else None

        base = target = None

        # ✅ Базова валута = най-близката до числото
        if amount_match:
            num_index = text.index(amount_match.group(1))
            closest_currency = None
            closest_distance = 999

            for word, code in self.currency_map.items():
                pos = text.find(word)
                if pos != -1:
                    if abs(pos - num_index) < closest_distance:
                        closest_distance = abs(pos - num_index)
                        closest_currency = code

            base = closest_currency

        # 👉 целевата валута = първата различна от base
        for word, code in self.currency_map.items():
            if word in text and code != base:
                target = code
                break

        if base and not target:
            target = "BGN" if base != "BGN" else "EUR"

        if base and target:
            await self.send_rate(message.channel, base, target, amount)

async def setup(bot: commands.Bot):
    await bot.add_cog(CurrencyCog(bot))































































































