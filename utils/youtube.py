import os
import requests
from datetime import datetime, timedelta
from dateutil import parser
import pytz

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"


def fetch_latest_video(channel_id: str) -> dict | None:
    endpoint = f"{BASE_URL}/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 1,
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    items = data.get("items", [])
    if not items:
        return None
    return items[0]


def fetch_all_videos(channel_id: str, max_results: int = 50) -> list:
    endpoint = f"{BASE_URL}/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 50,
        "type": "video",
    }
    videos = []
    page_count = 0
    max_pages = max_results // 50 + 1

    while True:
        response = requests.get(endpoint, params=params)
        data = response.json()

        for item in data.get("items", []):
            videos.append(item)
            if len(videos) >= max_results:
                return videos

        if "nextPageToken" in data and page_count < max_pages:
            params["pageToken"] = data["nextPageToken"]
            page_count += 1
        else:
            break

    return videos


def fetch_video_details(video_id: str) -> dict | None:
    endpoint = f"{BASE_URL}/videos"
    params = {
        "key": YOUTUBE_API_KEY,
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    items = data.get("items", [])
    if not items:
        return None
    return items[0]


def is_livestream(video: dict) -> bool:
    return "liveStreamingDetails" in video


def get_start_time(video: dict) -> str:
    try:
        start_time = video["liveStreamingDetails"]["scheduledStartTime"]
    except KeyError:
        start_time = video["liveStreamingDetails"].get("actualStartTime", "不明")

    dt = parser.parse(start_time)
    jst = pytz.timezone("Asia/Tokyo")
    return dt.astimezone(jst).strftime("%Y/%m/%d %H:%M")


def convert_to_jst(utc_time: str) -> str:
    dt = parser.parse(utc_time)
    jst = pytz.timezone("Asia/Tokyo")
    return dt.astimezone(jst).strftime("%Y/%m/%d %H:%M")
