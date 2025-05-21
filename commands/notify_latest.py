import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config
from utils.youtube import fetch_latest_video, fetch_video_details, is_livestream, get_start_time

class NotifyLatest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_latest", description="最新のYouTube動画を通知します。")
    async def notify_latest(self, interaction: discord.Interaction):
        config = load_config()
        success_count = 0

        for guild_id, data in config.items():
            youtube_channel_id = data.get("youtube_channel_id")
            discord_channel_id = data.get("discord_channel_id")

            if not youtube_channel_id or not discord_channel_id:
                continue

            video = await fetch_latest_video(youtube_channel_id)
            if not video or not video.get("videoId"):
                continue

            channel = self.bot.get_channel(int(discord_channel_id))
            if not channel:
                continue

            video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
            details = await fetch_video_details(video["videoId"])
            if not details:
                continue

            if is_livestream(details):
                start_time = get_start_time(details)
                await channel.send(f"🔴 ライブ配信が始まりました: {video['title']}\n開始時刻: {start_time}\n{video_url}")
            else:
                await channel.send(f"🆕 新しい動画が投稿されました: {video['title']}\n{video_url}")

            success_count += 1

        await interaction.response.send_message(
            f"✅ {success_count} 件のチャンネルに最新動画を通知しました。",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(NotifyLatest(bot))
