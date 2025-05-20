import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config
from utils.youtube import fetch_latest_video, is_livestream, get_start_time

class NotifyLatest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_latest", description="登録されたすべてのYouTubeチャンネルの最新動画を通知します。")
    async def notify_latest(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        config = load_config()
        count = 0

        for channel_id, discord_channel_id in config.items():
            video = fetch_latest_video(channel_id)
            if video is None:
                continue

            url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            title = video["snippet"]["title"]
            is_live = is_livestream(video)
            start_time = get_start_time(video)

            message = (
                f"🔴 **ライブ配信が始まりました！**\n{title}\n{url}\n開始時刻: {start_time}"
                if is_live else
                f"📢 **新しい動画が投稿されました！**\n{title}\n{url}"
            )

            channel = self.bot.get_channel(discord_channel_id)
            if channel:
                await channel.send(message)
                count += 1

        await interaction.followup.send(f"✅ {count} 件のチャンネルに最新動画を通知しました。")

async def setup(bot):
    await bot.add_cog(NotifyLatest(bot))
