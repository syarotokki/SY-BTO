import discord
from discord import app_commands
from discord.ext import commands
from utils.youtube import fetch_all_videos, is_livestream, get_start_time
from utils.config import load_config

class NotifyPast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="notify_past", description="過去のYouTube動画をすべて通知します。")
    async def notify_past(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        config = load_config()
        guild_id = str(interaction.guild_id)
        guild_config = config.get(guild_id)

        if not guild_config:
            await interaction.followup.send("❌ このサーバーは /subscribe または /set_config で設定されていません。")
            return

        yt_channel_id = guild_config.get("youtube_channel_id")
        channel_id = guild_config.get("channel_id")

        if not yt_channel_id or not channel_id:
            await interaction.followup.send("❌ YouTube チャンネル ID または 通知チャンネルが設定されていません。")
            return

        videos = fetch_all_videos(yt_channel_id)
        if not videos:
            await interaction.followup.send("❌ 過去動画の取得に失敗しました。")
            return

        notify_channel = interaction.guild.get_channel(int(channel_id))
        if not notify_channel:
            await interaction.followup.send("❌ 通知チャンネルが見つかりません。")
            return

        for video in reversed(videos):
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            title = video['snippet']['title']

            if is_livestream(video):
                start_time = get_start_time(video)
                msg = f"🔴 ライブ配信がありました：**{title}**\n{video_url}\n📅 開始時刻: {start_time}"
            else:
                msg = f"📺 過去の動画：**{title}**\n{video_url}"

            await notify_channel.send(msg)

        await interaction.followup.send(f"✅ {len(videos)} 件の動画を通知しました。")

async def setup(bot):
    await bot.add_cog(NotifyPast(bot))
