import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config
from utils.youtube import fetch_all_videos, fetch_video_details, is_livestream, get_start_time

class NotifyPast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_past", description="過去のYouTube動画を全て通知します。")
    async def notify_past(self, interaction: discord.Interaction):
        config = load_config()
        success_count = 0

        for guild_id, data in config.items():
            youtube_channel_id = data.get("youtube_channel_id")
            discord_channel_id = data.get("discord_channel_id")

            if not youtube_channel_id or not discord_channel_id:
                continue

            videos = await fetch_all_videos(youtube_channel_id)
            if not videos:
                continue

            channel = self.bot.get_channel(int(discord_channel_id))
            if not channel:
                continue

            for video in reversed(videos):  # 古い順に通知
                video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
                details = await fetch_video_details(video["videoId"])

                if is_livestream(details):
                    start_time = get_start_time(details)
                    await channel.send(f"🔴 ライブ配信（過去）: {video['title']}\n開始時刻: {start_time}\n{video_url}")
                else:
                    await channel.send(f"📼 過去の動画: {video['title']}\n{video_url}")

            success_count += 1

        await interaction.response.send_message(
            f"✅ {success_count} 件のチャンネルに過去動画を通知しました。",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(NotifyPast(bot))
