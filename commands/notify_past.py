import discord
from discord import app_commands
from discord.ext import commands
from utils.config import load_config
from utils.youtube import fetch_all_videos, is_livestream, get_start_time

class NotifyPast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_past", description="登録されたチャンネルの過去の動画をすべて通知します。")
    async def notify_past(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        config = load_config()
        count = 0

        for channel_id, discord_channel_id in config.items():
            videos = fetch_all_videos(channel_id)
            if not videos:
                continue

            for video in reversed(videos):  # 古い順に通知
                url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                title = video["snippet"]["title"]
                is_live = is_livestream(video)
                start_time = get_start_time(video)

                message = (
                    f"🔴 **ライブ配信がありました！**\n{title}\n{url}\n開始時刻: {start_time}"
                    if is_live else
                    f"📺 **過去の動画:**\n{title}\n{url}"
                )

                channel = self.bot.get_channel(discord_channel_id)
                if channel:
                    await channel.send(message)

            count += 1

        await interaction.followup.send(f"✅ {count} 件のチャンネルに過去動画を通知しました。")

async def setup(bot):
    await bot.add_cog(NotifyPast(bot))
