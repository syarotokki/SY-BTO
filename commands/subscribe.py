import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class Subscribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="subscribe", description="YouTubeチャンネルと通知先チャンネルを登録します。")
    @app_commands.describe(youtube_channel_id="YouTubeのチャンネルID", notification_channel="通知を送るDiscordチャンネル")
    async def subscribe(self, interaction: discord.Interaction, youtube_channel_id: str, notification_channel: discord.TextChannel):
        config = load_config()

        guild_id = str(interaction.guild.id)

        config[guild_id] = {
            "youtube_channel_id": youtube_channel_id,
            "notification_channel_id": notification_channel.id,
            "log_enabled": False,
            "log_channel_id": None
        }

        save_config(config)

        await interaction.response.send_message(
            f"✅ 通知設定を保存しました！\nYouTubeチャンネル: `{youtube_channel_id}`\n通知先: {notification_channel.mention}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Subscribe(bot))
