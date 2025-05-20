import os
import discord
from discord.ext import commands, tasks
from utils.config import load_config
from utils.youtube import fetch_latest_video, is_livestream, get_start_time
from keep_alive import keep_alive
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await tree.sync()
    check_new_videos.start()

@tasks.loop(minutes=5)
async def check_new_videos():
    config = load_config()
    for channel_id, discord_channel_id in config.items():
        video = fetch_latest_video(channel_id)
        if not video:
            continue

        video_id = video["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        title = video["snippet"]["title"]
        is_live = is_livestream(video)
        start_time = get_start_time(video)

        message = (
            f"🔴 **ライブ配信が始まりました！**\n{title}\n{url}\n開始時刻: {start_time}"
            if is_live else
            f"📢 **新しい動画が公開されました！**\n{title}\n{url}"
        )

        channel = bot.get_channel(discord_channel_id)
        if channel:
            async for msg in channel.history(limit=5):
                if video_id in msg.content:
                    break
            else:
                await channel.send(message)

async def main():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")

    keep_alive()
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
