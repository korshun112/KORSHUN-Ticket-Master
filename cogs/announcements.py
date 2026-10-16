import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.helpers import set_watermark
class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="announce", description="Отправить объявление в ЛС всем участникам сервера")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(title="Заголовок объявления (необязательно)", message="Текст объявления (\\n = перенос)")
    async def announce(self, interaction: discord.Interaction, message: str, title: str = None):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        members = [m for m in guild.members if not m.bot]
        embed_template = discord.Embed(
            title=title or "📢 Объявление",
            description=message.replace("\\n", "\n"),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        if guild.icon:
            embed_template.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed_template.set_author(name=guild.name)
        set_watermark(embed_template)
        sent = 0
        failed = 0
        progress_msg = await interaction.followup.send(
            f"📢 Начинаю рассылку по **{len(members)}** участникам...",
            ephemeral=True,
            wait=True
        )
        for i, member in enumerate(members, 1):
            try:
                await member.send(embed=embed_template.copy())
                sent += 1
            except (discord.Forbidden, discord.HTTPException):
                failed += 1
            await asyncio.sleep(0.7)
            if i % 25 == 0:
                try:
                    await progress_msg.edit(content=f"📢 Прогресс: {i}/{len(members)} | ✅ {sent} | ❌ {failed}")
                except discord.HTTPException:
                    pass
        result = discord.Embed(
            title="📢 Рассылка завершена",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        result.add_field(name="Всего", value=str(len(members)), inline=True)
        result.add_field(name="✅ Доставлено", value=str(sent), inline=True)
        result.add_field(name="❌ Не доставлено", value=str(failed), inline=True)
        set_watermark(result)
        try:
            await progress_msg.edit(content=None, embed=result)
        except discord.HTTPException:
            await interaction.followup.send(embed=result, ephemeral=True)
async def setup(bot):
    await bot.add_cog(Announcements(bot))
