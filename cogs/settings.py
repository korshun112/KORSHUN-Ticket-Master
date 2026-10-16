import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from database import DB_PATH
class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def _update_setting(self, interaction: discord.Interaction, column: str, value, success_msg: str):
        allowed = {
            "category_id", "log_channel_id", "support_role_id", "open_role_id",
            "close_role_id", "panel_title", "panel_description", "panel_color",
            "panel_image", "panel_thumbnail"
        }
        if column not in allowed:
            await interaction.response.send_message("❌ Недопустимая настройка.", ephemeral=True)
            return
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)", (interaction.guild.id,))
            await db.execute(f"UPDATE guild_settings SET {column} = ? WHERE guild_id = ?", (value, interaction.guild.id))
            await db.commit()
        await interaction.response.send_message(success_msg, ephemeral=True)
    @app_commands.command(name="config", description="Показать текущие настройки бота")
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT category_id, log_channel_id, support_role_id, open_role_id, close_role_id FROM guild_settings WHERE guild_id = ?",
                (interaction.guild.id,)
            ) as cursor:
                row = await cursor.fetchone()
        if not row:
            await interaction.response.send_message("❌ Настройки не найдены. Используйте `/setup_panel`.", ephemeral=True)
            return
        category_id, log_channel_id, support_role_id, open_role_id, close_role_id = row
        embed = discord.Embed(title="⚙️ Настройки KORSHUN Ticket Master", color=discord.Color.blurple())
        embed.add_field(name="Категория тикетов", value=f"<#{category_id}>" if category_id else "❌ Не задано", inline=False)
        embed.add_field(name="Канал логов", value=f"<#{log_channel_id}>" if log_channel_id else "❌ Не задано", inline=False)
        embed.add_field(name="Роль поддержки", value=f"<@&{support_role_id}>" if support_role_id else "❌ Не задано", inline=False)
        embed.add_field(name="Роль при открытии", value=f"<@&{open_role_id}>" if open_role_id else "❌ Не задано", inline=False)
        embed.add_field(name="Роль при закрытии", value=f"<@&{close_role_id}>" if close_role_id else "❌ Не задано", inline=False)
        embed.set_footer(text="Разработано студией KORSHUN BOTS")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="config_category", description="Категория Discord, где создаются тикеты")
    @app_commands.default_permissions(manage_guild=True)
    async def config_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        await self._update_setting(interaction, "category_id", category.id, f"✅ Категория тикетов: {category.mention}")
    @app_commands.command(name="config_logs", description="Канал для логов тикетов")
    @app_commands.default_permissions(manage_guild=True)
    async def config_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self._update_setting(interaction, "log_channel_id", channel.id, f"✅ Канал логов: {channel.mention}")
    @app_commands.command(name="config_support_role", description="Роль поддержки (пингуется при создании тикета)")
    @app_commands.default_permissions(manage_guild=True)
    async def config_support_role(self, interaction: discord.Interaction, role: discord.Role):
        await self._update_setting(interaction, "support_role_id", role.id, f"✅ Роль поддержки: {role.mention}")
    @app_commands.command(name="config_open_role", description="Роль, выдаваемая при открытии тикета")
    @app_commands.default_permissions(manage_guild=True)
    async def config_open_role(self, interaction: discord.Interaction, role: discord.Role):
        await self._update_setting(interaction, "open_role_id", role.id, f"✅ Роль при открытии: {role.mention}")
    @app_commands.command(name="config_close_role", description="Роль, выдаваемая при закрытии тикета (необязательно)")
    @app_commands.default_permissions(manage_guild=True)
    async def config_close_role(self, interaction: discord.Interaction, role: discord.Role):
        await self._update_setting(interaction, "close_role_id", role.id, f"✅ Роль при закрытии: {role.mention}")
    @app_commands.command(name="config_close_role_clear", description="Убрать роль, выдаваемую при закрытии тикета")
    @app_commands.default_permissions(manage_guild=True)
    async def config_close_role_clear(self, interaction: discord.Interaction):
        await self._update_setting(interaction, "close_role_id", None, "✅ Роль при закрытии убрана.")
    @app_commands.command(name="add_category", description="Добавить категорию тикетов")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(name="Название", emoji="Эмодзи (необязательно)", description="Описание (необязательно)")
    async def add_category(self, interaction: discord.Interaction, name: str, emoji: str = None, description: str = None):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO ticket_categories (guild_id, name, emoji, description) VALUES (?, ?, ?, ?)",
                (interaction.guild.id, name, emoji, description)
            )
            await db.commit()
        await interaction.response.send_message(f"✅ Категория **{name}** добавлена.", ephemeral=True)
    @app_commands.command(name="list_categories", description="Показать все категории тикетов")
    @app_commands.default_permissions(manage_guild=True)
    async def list_categories(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT id, name, emoji, description FROM ticket_categories WHERE guild_id = ?",
                (interaction.guild.id,)
            ) as cursor:
                cats = await cursor.fetchall()
        if not cats:
            await interaction.response.send_message("❌ Категорий нет. Добавьте `/add_category`.", ephemeral=True)
            return
        embed = discord.Embed(title="📋 Категории тикетов", color=discord.Color.blurple())
        for cid, name, emoji, desc in cats:
            embed.add_field(name=f"{emoji or ''} {name} (ID: {cid})", value=desc or "—", inline=False)
        embed.set_footer(text="Разработано студией KORSHUN BOTS")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="remove_category", description="Удалить категорию по ID")
    @app_commands.default_permissions(manage_guild=True)
    async def remove_category(self, interaction: discord.Interaction, category_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM ticket_categories WHERE id = ? AND guild_id = ?", (category_id, interaction.guild.id))
            await db.commit()
        await interaction.response.send_message(f"✅ Категория с ID {category_id} удалена.", ephemeral=True)
    @app_commands.command(name="set_panel_title", description="Установить заголовок панели")
    @app_commands.default_permissions(manage_guild=True)
    async def set_panel_title(self, interaction: discord.Interaction, title: str):
        await self._update_setting(interaction, "panel_title", title, "✅ Заголовок обновлён. Не забудьте `/refresh_panel`.")
    @app_commands.command(name="set_panel_description", description="Установить описание панели (\\n для переноса строки)")
    @app_commands.default_permissions(manage_guild=True)
    async def set_panel_description(self, interaction: discord.Interaction, description: str):
        text = description.replace("\\n", "\n")
        await self._update_setting(interaction, "panel_description", text, "✅ Описание обновлено. Не забудьте `/refresh_panel`.")
    @app_commands.command(name="set_panel_color", description="Установить цвет панели (формат #RRGGBB)")
    @app_commands.default_permissions(manage_guild=True)
    async def set_panel_color(self, interaction: discord.Interaction, color: str):
        try:
            discord.Color.from_str(color)
        except Exception:
            await interaction.response.send_message("❌ Неверный формат цвета. Пример: `#5865F2`", ephemeral=True)
            return
        await self._update_setting(interaction, "panel_color", color, "✅ Цвет обновлён. Не забудьте `/refresh_panel`.")
    @app_commands.command(name="set_panel_image", description="Установить изображение панели (URL)")
    @app_commands.default_permissions(manage_guild=True)
    async def set_panel_image(self, interaction: discord.Interaction, url: str):
        if not url.startswith(("http://", "https://")):
            await interaction.response.send_message("❌ URL должен начинаться с http:// или https://", ephemeral=True)
            return
        await self._update_setting(interaction, "panel_image", url, "✅ Изображение обновлено. Не забудьте `/refresh_panel`.")
    @app_commands.command(name="set_panel_thumbnail", description="Установить миниатюру панели (URL)")
    @app_commands.default_permissions(manage_guild=True)
    async def set_panel_thumbnail(self, interaction: discord.Interaction, url: str):
        if not url.startswith(("http://", "https://")):
            await interaction.response.send_message("❌ URL должен начинаться с http:// или https://", ephemeral=True)
            return
        await self._update_setting(interaction, "panel_thumbnail", url, "✅ Миниатюра обновлена. Не забудьте `/refresh_panel`.")
    @app_commands.command(name="help", description="Справка по командам KORSHUN Ticket Master")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 KORSHUN Ticket Master — команды",
            description="**Разработано студией KORSHUN BOTS**",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="⚙️ Настройка (админ)",
            value=(
                "`/setup_panel` — создать панель\n"
                "`/refresh_panel` — применить новые настройки\n"
                "`/config` — показать текущие настройки\n"
                "`/config_category` — категория Discord для тикетов\n"
                "`/config_logs` — канал логов\n"
                "`/config_support_role` — роль поддержки\n"
                "`/config_open_role` — роль при открытии\n"
                "`/config_close_role` — роль при закрытии\n"
                "`/config_close_role_clear` — убрать роль при закрытии"
            ),
            inline=False
        )
        embed.add_field(
            name="📂 Категории",
            value=(
                "`/add_category` — добавить категорию\n"
                "`/list_categories` — список\n"
                "`/remove_category` — удалить по ID"
            ),
            inline=False
        )
        embed.add_field(
            name="🎨 Кастомизация панели",
            value=(
                "`/set_panel_title` — заголовок\n"
                "`/set_panel_description` — описание (`\\n` = перенос)\n"
                "`/set_panel_color` — цвет (`#5865F2`)\n"
                "`/set_panel_image` — картинка (URL)\n"
                "`/set_panel_thumbnail` — миниатюра (URL)"
            ),
            inline=False
        )
        embed.add_field(
            name="📢 Дополнительное",
            value="`/announce` — рассылка ЛС всем участникам (админ)",
            inline=False
        )
        embed.set_footer(text="Разработано студией KORSHUN BOTS")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Settings(bot))
