import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config, save_config

class SetLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_log", description="ログチャンネルを設定・ログの送信をON/OFFします")
    @app_commands.describe(
        log_channel="ログを送信するチャンネル（未指定で無効化）",
        enable_logging="ログ送信を有効にするか（true / false）"
    )
    async def set_log(
        self,
        interaction: discord.Interaction,
        log_channel: discord.TextChannel = None,
        enable_logging: bool = None
    ):
        config = load_config()
        guild_id = str(interaction.guild_id)

        if guild_id not in config:
            await interaction.response.send_message(
                "❌ このサーバーはまだ /subscribe で設定されていません。",
                ephemeral=True
            )
            return

        # 初期化
        if log_channel is not None:
            config[guild_id]["log_channel_id"] = log_channel.id
        elif "log_channel_id" in config[guild_id]:
            del config[guild_id]["log_channel_id"]

        if enable_logging is not None:
            config[guild_id]["log_enabled"] = enable_logging

        save_config(config)

        # 応答内容の構築
        result = []
        if log_channel is not None:
            result.append(f"✅ ログチャンネルを <#{log_channel.id}> に設定しました。")
        elif log_channel is None and "log_channel_id" not in config[guild_id]:
            result.append("✅ ログチャンネルの設定を解除しました。")

        if enable_logging is not None:
            state = "有効" if enable_logging else "無効"
            result.append(f"✅ ログ送信を **{state}** に設定しました。")

        if not result:
            result.append("ℹ️ 変更はありませんでした。")

        await interaction.response.send_message(
            "\n".join(result),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SetLog(bot))
