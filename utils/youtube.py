import os
import requests
from datetime import datetime
from dateutil import parser
import pytz
import json

from utils.config import get_config, get_log_channel

YOUTUBE_API_KEYS = os.getenv("YOUTUBE_API_KEYS", "").split(",")

# タイムゾーンをJSTに設定
JST = pytz.timezone("Asia/Tokyo")

def get_valid_api_key():
    return YOUTUBE_API_KEYS

async def fetch_latest_video(channel_id, bot, guild_id):
    for api_key in get_valid_api_key():
        url = (
            f"https://www.googleapis.com/youtube/v3/search?key={api_key}"
            f"&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
        )
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            reason = data["error"]["errors"][0].get("reason", "unknown")
            log_channel_id = get_log_channel(guild_id)
            if log_channel_id:
                log_channel = bot.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(f"❌ APIキーが使用できませんでした（{api_key}）: {reason}")
            continue  # 次のキーを試す

        items = data.get("items", [])
        if not items:
            return None

        video = items[0]
        video_id = video["id"].get("videoId")
        if not video_id:
            return None

        video_details = await fetch_video_details(video_id, bot, guild_id)
        return video_details

    return None

async def fetch_video_details(video_id, bot, guild_id):
    for api_key in get_valid_api_key():
        url = (
            f"https://www.googleapis.com/youtube/v3/videos?part=snippet,liveStreamingDetails"
            f"&id={video_id}&key={api_key}"
        )
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            reason = data["error"]["errors"][0].get("reason", "unknown")
            log_channel_id = get_log_channel(guild_id)
            if log_channel_id:
                log_channel = bot.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(f"❌ 動画詳細取得時にAPIキーが使用できませんでした（{api_key}）: {reason}")
            continue

        items = data.get("items", [])
        if not items:
            return None

        item = items[0]
        return {
            "video_id": video_id,
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "is_live": "liveStreamingDetails" in item,
            "start_time": item.get("liveStreamingDetails", {}).get("scheduledStartTime")
        }

    return None

def is_livestream(video):
    return video.get("is_live", False)

def get_start_time(video):
    start_time_str = video.get("start_time")
    if not start_time_str:
        return "不明"
    dt = parser.parse(start_time_str)
    dt_jst = dt.astimezone(JST)
    return dt_jst.strftime("%Y/%m/%d %H:%M").replace(" ", "\n")

