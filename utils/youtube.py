import os
import requests
from datetime import datetime, timezone
import traceback

# 複数のAPIキーをカンマ区切りで取得
YOUTUBE_API_KEYS = os.getenv("YOUTUBE_API_KEYS", "").split(",")
KEY_INDEX = 0


def get_api_key():
    return YOUTUBE_API_KEYS[KEY_INDEX]


def switch_api_key():
    global KEY_INDEX
    KEY_INDEX = (KEY_INDEX + 1) % len(YOUTUBE_API_KEYS)
    print(f"[YouTube API] Switching to API key {KEY_INDEX + 1}/{len(YOUTUBE_API_KEYS)}")


def youtube_api_request(url, params):
    for _ in range(len(YOUTUBE_API_KEYS)):
        params["key"] = get_api_key()
        response = requests.get(url, params=params)
        data = response.json()

        # quota exceeded 対応
        if "error" in data:
            error = data["error"]["errors"][0]
            reason = error.get("reason", "")
            if reason == "quotaExceeded":
                print(f"[YouTube API] Quota exceeded for key {KEY_INDEX + 1}.")
                switch_api_key()
                continue
            else:
                print("[YouTube API] API error:", data["error"])
                return None
        return data
    print("[YouTube API] All API keys quota exceeded.")
    return None


def fetch_latest_video(channel_id):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 1,
    }
    data = youtube_api_request(url, params)
    if not data or "items" not in data or len(data["items"]) == 0:
        return None
    return data["items"][0]


def fetch_all_videos(channel_id, max_results=50):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": max_results,
    }
    data = youtube_api_request(url, params)
    if not data or "items" not in data:
        return []
    return data["items"]


def is_livestream(video_data):
    snippet = video_data.get("snippet", {})
    return snippet.get("liveBroadcastContent") == "live"


def get_start_time(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "id": video_id,
        "part": "liveStreamingDetails",
    }
    data = youtube_api_request(url, params)
    if not data or "items" not in data or len(data["items"]) == 0:
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
        except Exception:
            print("Failed to send log message:", message)
            traceback.print_exc()
