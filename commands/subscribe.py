import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class Subscribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="subscribe", description="YouTubeチャンネルと通知チャンネルを設定します")
    @app_commands.describe(channel_id="YouTubeのチャンネルID", notify_channel="通知を送るDiscordチャンネル")
    async def subscribe(self, interaction: discord.Interaction, channel_id: str, notify_channel: discord.TextChannel):
        config = load_config()
        config[str(interaction.guild_id)] = {
            "youtube_channel_id": channel_id,
            "notify_channel_id": notify_channel.id
        }
        save_config(config)
        await interaction.response.send_message(
            f"✅ 登録しました。\nYouTubeチャンネルID: `{channel_id}`\n通知チャンネル: {notify_channel.mention}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Subscribe(bot))
