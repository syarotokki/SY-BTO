import requests
import os
from datetime import datetime, timezone

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def fetch_latest_video(channel_id):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 1,
        "type": "video",
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    items = data.get("items", [])
    if not items:
        return None
    return items[0]


def fetch_all_videos(channel_id):
    videos = []
    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 50,
        "type": "video",
    }

    while True:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        videos.extend(data.get("items", []))

        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
        else:
            break

    return videos


def is_livestream(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": YOUTUBE_API_KEY,
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return False

    items = response.json().get("items", [])
    if not items:
        return False

    return "liveStreamingDetails" in items[0]


def get_start_time(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": YOUTUBE_API_KEY,
        "id": video_id,
        "part": "liveStreamingDetails",
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None

    items = response.json().get("items", [])
    if not items:
        return None

    live_details = items[0].get("liveStreamingDetails", {})
    start_time_str = live_details.get("actualStartTime")
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        return start_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return None

