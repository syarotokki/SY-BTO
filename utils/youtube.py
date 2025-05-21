import os
import requests
from datetime import datetime, timezone
import traceback

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def fetch_latest_video(channel_id):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 1,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        return None

    return data["items"][0]


def fetch_all_videos(channel_id, max_results=50):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": max_results,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data:
        return []

    return data["items"]


def is_livestream(video_data):
    snippet = video_data.get("snippet", {})
    live_broadcast_content = snippet.get("liveBroadcastContent")
    return live_broadcast_content == "live"


def get_start_time(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": YOUTUBE_API_KEY,
        "id": video_id,
        "part": "liveStreamingDetails",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        return None

    details = data["items"][0].get("liveStreamingDetails", {})
    start_time_str = details.get("actualStartTime")
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        return start_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return None


async def send_log(interaction, message):
    try:
        await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        try:
            await interaction.followup.send(message, ephemeral=True)
        except Exception as e:
            print("Failed to send log message:", message)
            traceback.print_exc()

