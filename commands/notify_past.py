import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config
from utils.youtube import (
    fetch_all_videos,
    fetch_video_details,
    is_livestream,
    get_start_time,
    convert_to_jst,
)

class NotifyPastCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_past", description="過去の動画を通知します。")
    async def notify_past(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        config = load_config()
        notified_count = 0

        for channel_id, discord_channel_id in config.items():
            videos = fetch_all_videos(channel_id, max_results=100)
            if not videos:
                continue

            discord_channel = self.bot.get_channel(discord_channel_id)
            if not discord_channel:
                continue

            for video in reversed(videos):
                video_id = video["id"]["videoId"]
                details = fetch_video_details(video_id)
                if not details:
                    continue

                title = details["snippet"]["title"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                published_at = convert_to_jst(details["snippet"]["publishedAt"])

                if is_livestream(details):
                    start_time = get_start_time(details)
                    message = f"🔴 ライブ配信が始まりました！\n**{title}**\n開始時刻：{start_time}\n{url}"
                else:
                    message = f"📺 新しい動画が公開されました！\n**{title}**\n公開日時：{published_at}\n{url}"

                await discord_channel.send(message)

            notified_count += 1

        await interaction.followup.send(f"✅ {notified_count} 件のチャンネルに過去動画を通知しました。")


async def setup(bot: commands.Bot):
    await bot.add_cog(NotifyPastCommand(bot))
