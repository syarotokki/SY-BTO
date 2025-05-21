import os
import requests
from datetime import datetime, timezone
import traceback
import itertools

# 複数APIキーを取得・ローテーション用
YOUTUBE_API_KEYS = os.getenv("YOUTUBE_API_KEYS", "").split(",")
api_key_cycle = itertools.cycle(YOUTUBE_API_KEYS)

def get_next_api_key():
    return next(api_key_cycle)


def fetch_latest_video(channel_id):
    for _ in range(len(YOUTUBE_API_KEYS)):
        api_key = get_next_api_key()
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": 1,
        }
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200 and "items" in data and len(data["items"]) > 0:
            return data["items"][0]
        elif "error" in data:
            print(f"[API key {api_key}] YouTube API error:", data["error"].get("message"))

    return None


def fetch_all_videos(channel_id, max_results=50):
    for _ in range(len(YOUTUBE_API_KEYS)):
        api_key = get_next_api_key()
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": max_results,
        }
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200 and "items" in data:
            return data["items"]
        elif "error" in data:
            print(f"[API key {api_key}] YouTube API error:", data["error"].get("message"))

    return []


def is_livestream(video_data):
    snippet = video_data.get("snippet", {})
    return snippet.get("liveBroadcastContent") == "live"


def get_start_time(video_id):
    for _ in range(len(YOUTUBE_API_KEYS)):
        api_key = get_next_api_key()
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "key": api_key,
            "id": video_id,
            "part": "liveStreamingDetails",
        }
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200 and "items" in data and len(data["items"]) > 0:
            details = data["items"][0].get("liveStreamingDetails", {})
            start_time_str = details.get("actualStartTime")
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                return start_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        elif "error" in data:
            print(f"[API key {api_key}] YouTube API error:", data["error"].get("message"))

    return None


async def send_log(interaction, message):
    try:
        await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        try:
            await interaction.followup.send(message, ephemeral=True)
        except Exception:
            print("Failed to send log message:", message)
            traceback.print_exc()
