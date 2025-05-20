import os
import requests
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("bot")

api_keys = [key.strip() for key in os.getenv("YOUTUBE_API_KEY", "").split(",") if key.strip()]
if not api_keys:
    raise ValueError("❌ YOUTUBE_API_KEY が設定されていません。")

def fetch_youtube_data(url_params: dict) -> dict:
    for i, api_key in enumerate(api_keys):
        params = dict(url_params)
        params["key"] = api_key

        try:
            response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
            data = response.json()

            if response.status_code == 200:
                return data

            if "error" in data:
                reason = data["error"]["errors"][0].get("reason", "")
                if reason == "quotaExceeded":
                    logger.warning(f"⚠️ APIキー {i+1}/{len(api_keys)} がクォータ超過。次を試します。")
                    continue
                else:
                    logger.error(f"❌ YouTube APIエラー: {data['error']}")
                    raise Exception(f"YouTube API error: {data['error']}")
        except requests.RequestException as e:
            logger.exception("❌ YouTube APIリクエストエラー")
            raise e

    raise RuntimeError("❌ 全てのAPIキーが quotaExceeded です。")

def fetch_latest_video(channel_id: str):
    url_params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "maxResults": 1,
        "type": "video"
    }
    data = fetch_youtube_data(url_params)
    items = data.get("items", [])
    return items[0] if items else None

def fetch_all_videos(channel_id: str):
    videos = []
    next_page_token = None

    while True:
        url_params = {
            "part": "snippet",
            "channelId": channel_id,
            "order": "date",
            "maxResults": 50,
            "type": "video",
        }
        if next_page_token:
            url_params["pageToken"] = next_page_token

        data = fetch_youtube_data(url_params)
        items = data.get("items", [])
        if not items:
            break

        videos.extend(items)
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def is_livestream(video):
    return "live" in video["snippet"].get("liveBroadcastContent", "").lower()

def get_start_time(video):
    published_at = video["snippet"]["publishedAt"]
    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    jst = dt.astimezone(timezone(timedelta(hours=9)))
    return jst.strftime("%Y/%m/%d %H:%M:%S")
