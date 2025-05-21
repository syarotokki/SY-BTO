import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="現在の設定を表示します")
    async def info(self, interaction: discord.Interaction):
        config = load_config()
        guild_id = str(interaction.guild.id)
        guild_config = config.get(guild_id)

        if not guild_config:
            await interaction.response.send_message("⚠️ このサーバーではまだ `/subscribe` が設定されていません。", ephemeral=True)
            return

        channel_id = guild_config.get("channel_id")
        youtube_channel_id = guild_config.get("youtube_channel_id")
        log_channel_id = guild_config.get("log_channel_id")

        embed = discord.Embed(title="📄 現在の設定", color=discord.Color.blue())
        embed.add_field(name="YouTube チャンネルID", value=youtube_channel_id or "未設定", inline=False)
        embed.add_field(name="通知チャンネル", value=f"<#{channel_id}>" if channel_id else "未設定", inline=False)
        embed.add_field(name="ログチャンネル", value=f"<#{log_channel_id}>" if log_channel_id else "未設定", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Info(bot))
