import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class Subscribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="subscribe", description="YouTubeチャンネルIDと通知先チャンネルを設定します。")
    @app_commands.describe(youtube_channel_id="YouTubeのチャンネルID（例: UCxxxxxxx）")
    async def subscribe(self, interaction: discord.Interaction, youtube_channel_id: str):
        config = load_config()
        guild_id = str(interaction.guild_id)
        channel_id = interaction.channel.id

        config[guild_id] = {
            "youtube_channel_id": youtube_channel_id,
            "discord_channel_id": str(channel_id)
        }

        save_config(config)
        await interaction.response.send_message(
            f"✅ 通知設定が完了しました！\nYouTubeチャンネルID: `{youtube_channel_id}`\n通知先: <#{channel_id}>",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Subscribe(bot))
