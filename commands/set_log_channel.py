import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class SetLogChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_log_channel", description="ログ出力用のチャンネルを設定します")
    @app_commands.describe(channel="ログ出力チャンネル")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        config = load_config()
        guild_id = str(interaction.guild.id)

        if guild_id not in config:
            await interaction.response.send_message("⚠️ このサーバーではまだ `/subscribe` が設定されていません。", ephemeral=True)
            return

        config[guild_id]["log_channel_id"] = channel.id
        save_config(config)

        await interaction.response.send_message(f"✅ ログチャンネルを <#{channel.id}> に設定しました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetLogChannel(bot))
