import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import init_db
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN не задан в .env или переменных окружения!")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
class KorshunBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        await init_db()
        from views.panel import PanelView
        from views.ticket import TicketControlView
        self.add_view(PanelView())
        self.add_view(TicketControlView())
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.settings")
        await self.load_extension("cogs.announcements")
        await self.tree.sync()
        print("✅ Слэш-команды синхронизированы")
    async def on_ready(self):
        print(f"🤖 KORSHUN Ticket Master запущен как {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="за тикетами | KORSHUN BOTS")
        )
bot = KorshunBot()
bot.run(TOKEN)
