import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
from database import DB_PATH
from utils.helpers import set_watermark
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="setup_panel", description="Создать панель тикетов в указанном канале")
    @app_commands.describe(channel="Канал, где будет размещена панель тикетов")
    @app_commands.default_permissions(manage_guild=True)
    async def setup_panel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        from views.panel import PanelView
        embed = await build_panel_embed(interaction.guild.id)
        try:
            msg = await channel.send(embed=embed, view=PanelView())
        except discord.Forbidden:
            await interaction.followup.send("❌ У бота нет прав писать в этот канал.", ephemeral=True)
            return
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)", (interaction.guild.id,))
            await db.execute(
                "UPDATE guild_settings SET panel_channel_id = ?, panel_message_id = ? WHERE guild_id = ?",
                (channel.id, msg.id, interaction.guild.id)
            )
            await db.commit()
        await interaction.followup.send(f"✅ Панель создана в {channel.mention}", ephemeral=True)
    @app_commands.command(name="refresh_panel", description="Обновить панель тикетов (применить новые настройки)")
    @app_commands.default_permissions(manage_guild=True)
    async def refresh_panel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT panel_channel_id, panel_message_id FROM guild_settings WHERE guild_id = ?",
                (interaction.guild.id,)
            ) as cursor:
                row = await cursor.fetchone()
        if not row or not row[0] or not row[1]:
            await interaction.followup.send("❌ Панель ещё не создана. Используйте `/setup_panel`.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(row[0])
        if not channel:
            await interaction.followup.send("❌ Канал панели не найден.", ephemeral=True)
            return
        try:
            msg = await channel.fetch_message(row[1])
        except discord.NotFound:
            await interaction.followup.send("❌ Сообщение панели не найдено. Создайте заново `/setup_panel`.", ephemeral=True)
            return
        embed = await build_panel_embed(interaction.guild.id)
        await msg.edit(embed=embed)
        await interaction.followup.send("✅ Панель обновлена.", ephemeral=True)
async def build_panel_embed(guild_id: int) -> discord.Embed:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT panel_title, panel_description, panel_color, panel_image, panel_thumbnail FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
    title = row[0] if row and row[0] else "🎫 Поддержка"
    description = row[1] if row and row[1] else "Нажмите кнопку ниже, чтобы создать тикет."
    color_str = row[2] if row and row[2] else "#5865F2"
    image = row[3] if row else None
    thumbnail = row[4] if row else None
    try:
        color = discord.Color.from_str(color_str)
    except Exception:
        color = discord.Color.blurple()
    embed = discord.Embed(title=title, description=description, color=color)
    if image:
        embed.set_image(url=image)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    set_watermark(embed)
    return embed
async def create_ticket_channel(interaction: discord.Interaction, category_name: str, subject: str, details: str):
    guild = interaction.guild
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT category_id, support_role_id, open_role_id, log_channel_id, ticket_counter FROM guild_settings WHERE guild_id = ?",
            (guild.id,)
        ) as cursor:
            row = await cursor.fetchone()
        if not row or not row[0]:
            await interaction.followup.send(
                "❌ Категория Discord для тикетов не настроена. Используйте `/config_category`.",
                ephemeral=True
            )
            return
        category_id, support_role_id, open_role_id, log_channel_id, counter = row
        counter = counter or 0
        category = guild.get_channel(category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("❌ Настроенная категория не найдена.", ephemeral=True)
            return
        async with db.execute(
            "SELECT channel_id FROM tickets WHERE guild_id = ? AND user_id = ? AND status = 'open'",
            (guild.id, interaction.user.id)
        ) as cursor:
            existing = await cursor.fetchone()
        if existing:
            ch = guild.get_channel(existing[0])
            if ch:
                await interaction.followup.send(f"❌ У вас уже есть открытый тикет: {ch.mention}", ephemeral=True)
                return
        new_counter = counter + 1
        channel_name = f"ticket-{new_counter:04d}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True, send_messages=True,
                attach_files=True, read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True,
                manage_channels=True, manage_permissions=True
            )
        }
        if support_role_id:
            support_role = guild.get_role(support_role_id)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True,
                    attach_files=True, read_message_history=True
                )
        try:
            ticket_channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"Тикет {interaction.user} | {category_name}",
                reason=f"KORSHUN Ticket Master: {interaction.user}"
            )
        except discord.Forbidden:
            await interaction.followup.send("❌ Нет прав создать канал. Проверьте права бота.", ephemeral=True)
            return
        await db.execute(
            "INSERT INTO tickets (guild_id, channel_id, user_id, category, subject, status) VALUES (?, ?, ?, ?, ?, 'open')",
            (guild.id, ticket_channel.id, interaction.user.id, category_name, subject)
        )
        await db.execute(
            "UPDATE guild_settings SET ticket_counter = ? WHERE guild_id = ?",
            (new_counter, guild.id)
        )
        await db.commit()
    if open_role_id:
        role = guild.get_role(open_role_id)
        if role and role < guild.me.top_role:
            try:
                await interaction.user.add_roles(role, reason="KORSHUN Ticket Master: открытие тикета")
            except discord.Forbidden:
                pass
    ping_content = interaction.user.mention
    if support_role_id:
        ping_content += f" <@&{support_role_id}>"
    embed = discord.Embed(
        title=f"🎫 {category_name} — {subject}",
        description=details,
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Автор", value=interaction.user.mention, inline=True)
    embed.add_field(name="Категория", value=category_name, inline=True)
    set_watermark(embed)
    from views.ticket import TicketControlView
    await ticket_channel.send(content=ping_content, embed=embed, view=TicketControlView())
    await interaction.followup.send(f"✅ Тикет создан: {ticket_channel.mention}", ephemeral=True)
    if log_channel_id:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="📥 Тикет открыт",
                description=(
                    f"**Канал:** {ticket_channel.mention}\n"
                    f"**Автор:** {interaction.user.mention}\n"
                    f"**Категория:** {category_name}\n"
                    f"**Тема:** {subject}"
                ),
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            set_watermark(log_embed)
            try:
                await log_channel.send(embed=log_embed)
            except discord.Forbidden:
                pass
async def close_ticket_logic(interaction: discord.Interaction):
    guild = interaction.guild
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, subject FROM tickets WHERE channel_id = ? AND status = 'open'",
            (interaction.channel.id,)
        ) as cursor:
            ticket_row = await cursor.fetchone()
        if not ticket_row:
            await interaction.followup.send("❌ Это не активный тикет.", ephemeral=True)
            return
        user_id, subject = ticket_row
        async with db.execute(
            "SELECT close_role_id, open_role_id, log_channel_id FROM guild_settings WHERE guild_id = ?",
            (guild.id,)
        ) as cursor:
            settings = await cursor.fetchone()
        await db.execute(
            "UPDATE tickets SET status = 'closed' WHERE channel_id = ?",
            (interaction.channel.id,)
        )
        await db.commit()
    close_role_id, open_role_id, log_channel_id = settings if settings else (None, None, None)
    member = guild.get_member(user_id)
    if member:
        if open_role_id:
            role = guild.get_role(open_role_id)
            if role and role < guild.me.top_role and role in member.roles:
                try:
                    await member.remove_roles(role, reason="KORSHUN Ticket Master: закрытие тикета")
                except discord.Forbidden:
                    pass
        if close_role_id:
            role = guild.get_role(close_role_id)
            if role and role < guild.me.top_role:
                try:
                    await member.add_roles(role, reason="KORSHUN Ticket Master: закрытие тикета")
                except discord.Forbidden:
                    pass
        try:
            dm_embed = discord.Embed(
                title="🔒 Ваш тикет закрыт",
                description=(
                    f"Тикет **«{subject}»** был закрыт сотрудником **{interaction.user.display_name}**.\n\n"
                    f"Если проблема осталась — создайте новый тикет."
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            set_watermark(dm_embed)
            await member.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass
    if log_channel_id:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="📤 Тикет закрыт",
                description=(
                    f"**Канал:** {interaction.channel.name}\n"
                    f"**Автор:** <@{user_id}>\n"
                    f"**Закрыл:** {interaction.user.mention}\n"
                    f"**Тема:** {subject}"
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            set_watermark(log_embed)
            try:
                await log_channel.send(embed=log_embed)
            except discord.Forbidden:
                pass
    await interaction.followup.send("🔒 Тикет закрыт. Канал удалится через 5 секунд.")
    await asyncio.sleep(5)
    try:
        await interaction.channel.delete(reason="KORSHUN Ticket Master: закрытие тикета")
    except discord.Forbidden:
        pass
async def setup(bot):
    await bot.add_cog(Tickets(bot))
