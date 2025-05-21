import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class Subscribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="subscribe", description="YouTubeチャンネルと通知チャンネルを設定")
    @app_commands.describe(
        youtube_channel_id="YouTubeのチャンネルID（例：UCxxxxxx）",
        notify_channel="通知を送るDiscordチャンネル"
    )
    async def subscribe(
        self,
        interaction: discord.Interaction,
        youtube_channel_id: str,
        notify_channel: discord.TextChannel
    ):
        config = load_config()
        guild_id = str(interaction.guild_id)

        config[guild_id] = {
            "channel_id": notify_channel.id,
            "youtube_channel_id": youtube_channel_id,
            "log_enabled": False,
            "log_channel_id": None
        }
        save_config(config)

        await interaction.response.send_message(
            f"✅ 通知チャンネル: {notify_channel.mention}\n✅ YouTubeチャンネルID: `{youtube_channel_id}` を登録しました。",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Subscribe(bot))
