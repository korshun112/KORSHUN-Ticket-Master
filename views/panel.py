import discord
from discord import ui
import aiosqlite
from database import DB_PATH
from utils.helpers import set_watermark
class PanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(
        label="Создать тикет",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="korshun_create_ticket"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT id, name, emoji, description FROM ticket_categories WHERE guild_id = ?",
                (interaction.guild.id,)
            ) as cursor:
                cats = await cursor.fetchall()
        if not cats:
            await interaction.response.send_message(
                "❌ Категории не настроены. Попросите администратора добавить их командой `/add_category`.",
                ephemeral=True
            )
            return
        options = []
        for cid, name, emoji, desc in cats[:25]:
            opt_kwargs = {
                "label": name[:100],
                "value": str(cid),
                "description": (desc or "")[:100] or None
            }
            if emoji:
                try:
                    opt_kwargs["emoji"] = emoji
                except Exception:
                    pass
            options.append(discord.SelectOption(**opt_kwargs))
        view = ui.View(timeout=120)
        view.add_item(CategorySelect(options))
        await interaction.response.send_message("🎫 Выберите категорию тикета:", view=view, ephemeral=True)
class CategorySelect(ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Выберите категорию...", options=options)
    async def callback(self, interaction: discord.Interaction):
        category_id = int(self.values[0])
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT name FROM ticket_categories WHERE id = ?",
                (category_id,)
            ) as cursor:
                row = await cursor.fetchone()
        category_name = row[0] if row else "Тикет"

        await interaction.response.send_modal(TicketModal(category_name))
class TicketModal(ui.Modal):
    def __init__(self, category_name: str):
        super().__init__(title=f"Тикет: {category_name}"[:45])
        self.category_name = category_name
        self.subject = ui.TextInput(
            label="Тема",
            placeholder="Кратко опишите проблему",
            max_length=100
        )
        self.details = ui.TextInput(
            label="Детали",
            style=discord.TextStyle.paragraph,
            placeholder="Подробно опишите ситуацию",
            max_length=1500,
            required=False
        )
        self.add_item(self.subject)
        self.add_item(self.details)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        from cogs.tickets import create_ticket_channel
        await create_ticket_channel(
            interaction,
            self.category_name,
            self.subject.value,
            self.details.value or "Не указано"
        )
