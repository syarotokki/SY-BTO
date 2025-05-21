import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = "config.json"

class Subscribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="subscribe", description="YouTubeチャンネルの通知設定を行います")
    @app_commands.describe(youtube_channel_id="通知対象のYouTubeチャンネルID")
    async def subscribe(self, interaction: discord.Interaction, youtube_channel_id: str):
        await interaction.response.defer(thinking=True)

        guild_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)

        # config.json を読み込む（なければ空の辞書を用意）
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        else:
            config = {}

        # ギルドごとの設定を更新
        config[guild_id] = {
            "channel_id": channel_id,
            "youtube_channel_id": youtube_channel_id
        }

        # ここでデバッグ出力
        print("[DEBUG] Updated config:", config)

        # config.json に保存
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

        await interaction.followup.send(
            f"✅ 通知チャンネル: <#{channel_id}>\n📺 YouTubeチャンネルID: `{youtube_channel_id}` に設定しました。",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Subscribe(bot))
