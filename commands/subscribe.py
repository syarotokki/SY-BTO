import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class Subscribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="subscribe", description="YouTubeチャンネルのIDと通知チャンネルを登録します。")
    @app_commands.describe(channel_id="YouTubeチャンネルID", notify_channel="通知するDiscordチャンネル")
    async def subscribe(self, interaction: discord.Interaction, channel_id: str, notify_channel: discord.TextChannel):
        config = load_config()
        config[channel_id] = notify_channel.id
        save_config(config)
        await interaction.response.send_message(f"✅ チャンネル <#{notify_channel.id}> に YouTubeチャンネル `{channel_id}` の通知を設定しました。")

async def setup(bot):
    await bot.add_cog(Subscribe(bot))
