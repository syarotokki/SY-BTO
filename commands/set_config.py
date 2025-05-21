import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

class SetConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_config", description="通知・ログ設定をまとめて行います。")
    @app_commands.describe(
        youtube_channel_id="通知対象のYouTubeチャンネルID",
        notification_channel="YouTube動画を通知するチャンネル",
        log_channel="ログを送信するチャンネル（任意）",
        enable_logs="ログ送信を有効にするか（True/False）"
    )
    async def set_config(
        self,
        interaction: discord.Interaction,
        youtube_channel_id: str,
        notification_channel: discord.TextChannel,
        log_channel: discord.TextChannel = None,
        enable_logs: bool = False
    ):
        config = load_config()
        guild_id = str(interaction.guild_id)

        config[guild_id] = {
            "youtube_channel_id": youtube_channel_id,
            "channel_id": str(notification_channel.id),
            "log_channel_id": str(log_channel.id) if log_channel else None,
            "enable_logs": enable_logs
        }

        save_config(config)

        msg = f"✅ 設定を更新しました。\n\n"
        msg += f"- YouTube チャンネルID: `{youtube_channel_id}`\n"
        msg += f"- 通知チャンネル: {notification_channel.mention}\n"
        msg += f"- ログチャンネル: {log_channel.mention if log_channel else '未設定'}\n"
        msg += f"- ログ送信: {'有効' if enable_logs else '無効'}"

        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetConfig(bot))
