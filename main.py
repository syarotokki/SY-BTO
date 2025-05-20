import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio
import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

command_folder = "commands"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def main():
    async with bot:
        for filename in os.listdir(command_folder):
            if filename.endswith(".py"):
                await bot.load_extension(f"{command_folder}.{filename[:-3]}")
        keep_alive.keep_alive()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
