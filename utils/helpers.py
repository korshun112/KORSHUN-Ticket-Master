import discord
WATERMARK_TEXT = "Разработано студией KORSHUN BOTS"
def set_watermark(embed: discord.Embed) -> discord.Embed:
    embed.set_footer(text=WATERMARK_TEXT)
    return embed
