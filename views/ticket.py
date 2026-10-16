import discord
from discord import ui
import aiosqlite
from database import DB_PATH
from utils.helpers import set_watermark
class TicketControlView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(
        label="Рассмотреть тикет",
        style=discord.ButtonStyle.success,
        emoji="👀",
        custom_id="korshun_review_ticket"
    )
    async def review_ticket(self, interaction: discord.Interaction, button: ui.Button):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT support_role_id FROM guild_settings WHERE guild_id = ?",
                (interaction.guild.id,)
            ) as cursor:
                settings_row = await cursor.fetchone()
            async with db.execute(
                "SELECT user_id, subject FROM tickets WHERE channel_id = ?",
                (interaction.channel.id,)
            ) as cursor:
                ticket_row = await cursor.fetchone()
        if not ticket_row:
            await interaction.response.send_message("❌ Это не активный тикет.", ephemeral=True)
            return
        user_id, subject = ticket_row
        support_role_id = settings_row[0] if settings_row else None
        support_role = interaction.guild.get_role(support_role_id) if support_role_id else None
        is_staff = interaction.user.guild_permissions.administrator
        if support_role and support_role in interaction.user.roles:
            is_staff = True
        if not is_staff:
            await interaction.response.send_message(
                "❌ Только роль поддержки может взять тикет в рассмотрение.",
                ephemeral=True
            )
            return
        member = interaction.guild.get_member(user_id)
        dm_sent = False
        if member:
            try:
                dm_embed = discord.Embed(
                    title="👀 Ваш тикет взят в рассмотрение",
                    description=(
                        f"Ваш тикет **«{subject}»** был взят в рассмотрение "
                        f"сотрудником поддержки **{interaction.user.display_name}**.\n\n"
                        f"Ожидайте ответа в канале тикета."
                    ),
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                set_watermark(dm_embed)
                await member.send(embed=dm_embed)
                dm_sent = True
            except (discord.Forbidden, discord.HTTPException):
                pass
        embed = discord.Embed(
            title="👀 Тикет взят в рассмотрение",
            description=f"Сотрудник {interaction.user.mention} взял этот тикет в рассмотрение.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        set_watermark(embed)
        msg = ""
        if not dm_sent:
            msg = "⚠️ Не удалось отправить ЛС создателю тикета (у него закрыты ЛС)."
        await interaction.response.send_message(content=msg or None, embed=embed)
    @ui.button(
        label="Закрыть тикет",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="korshun_close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        from cogs.tickets import close_ticket_logic
        await close_ticket_logic(interaction)
