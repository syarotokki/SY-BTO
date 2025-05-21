import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config
from utils.youtube import fetch_latest_video, is_livestream, get_start_time, send_log

class NotifyLatest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_latest", description="最新動画またはライブ配信を通知します")
    async def notify_latest(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        config = load_config()
        guild_config = config.get(str(interaction.guild_id))

        if not guild_config or "youtube_channel_id" not in guild_config or "notify_channel_id" not in guild_config:
            await interaction.followup.send("❌ YouTube チャンネル ID または 通知チャンネルが設定されていません。", ephemeral=True)
            return

        channel_id = guild_config["youtube_channel_id"]
        notify_channel_id = guild_config["notify_channel_id"]
        log_channel_id = guild_config.get("log_channel_id")
        log_enabled = guild_config.get("log_enabled", False)

        try:
            video = fetch_latest_video(channel_id)
        except Exception as e:
            if log_enabled and log_channel_id:
                await send_log(self.bot, log_channel_id, f"❌ 最新動画の取得に失敗しました。\nエラー内容: `{str(e)}`")
            await interaction.followup.send("❌ 最新動画の取得に失敗しました。", ephemeral=True)
            return

        notify_channel = self.bot.get_channel(int(notify_channel_id))
        if not notify_channel:
            await interaction.followup.send("❌ 通知チャンネルが見つかりません。", ephemeral=True)
            return

        video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
        if is_livestream(video):
            start_time = get_start_time(video)
            message = f"🔴 ライブ配信が始まりました！\n**{video['title']}**\n開始時刻: {start_time}\n{video_url}"
        else:
            message = f"📺 新しい動画が投稿されました！\n**{video['title']}**\n{video_url}"

        await notify_channel.send(message)
        await interaction.followup.send("✅ 最新動画を通知しました。", ephemeral=True)

        if log_enabled and log_channel_id:
            await send_log(self.bot, log_channel_id, f"✅ 最新動画を通知しました。\nURL: {video_url}")

async def setup(bot):
    await bot.add_cog(NotifyLatest(bot))

