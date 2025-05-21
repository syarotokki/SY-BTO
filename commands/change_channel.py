import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class ChangeChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="change_channel", description="通知先のチャンネルを変更します")
    @app_commands.describe(channel="新しい通知チャンネル")
    async def change_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        config = load_config()
        guild_id = str(interaction.guild.id)

        if guild_id not in config:
            await interaction.response.send_message("⚠️ このサーバーではまだ `/subscribe` が設定されていません。", ephemeral=True)
            return

        config[guild_id]["channel_id"] = channel.id
        save_config(config)

        await interaction.response.send_message(f"✅ 通知チャンネルを <#{channel.id}> に変更しました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChangeChannel(bot))
