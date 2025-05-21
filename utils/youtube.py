import os
import random
import requests
from dateutil import parser
from datetime import datetime
import pytz
from utils.config import load_config, save_config

API_KEYS = os.getenv("YOUTUBE_API_KEY", "").split(",")

def fetch_latest_video(channel_id):
    for api_key in API_KEYS:
        try:
            url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "items" not in data or not data["items"]:
                send_log(f"⚠️ APIキー `{api_key[:8]}...` では動画が取得できませんでした。")
                continue
            return data["items"][0]
        except Exception as e:
            send_log(f"❌ APIキー `{api_key[:8]}...` での fetch_latest_video に失敗: {e}")
    return None

def fetch_all_videos(channel_id, max_results=10):
    for api_key in API_KEYS:
        try:
            url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults={max_results}"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "items" not in data:
                send_log(f"⚠️ APIキー `{api_key[:8]}...` では過去動画が取得できませんでした。")
                continue
            return data["items"]
        except Exception as e:
            send_log(f"❌ APIキー `{api_key[:8]}...` での fetch_all_videos に失敗: {e}")
    return []

def is_livestream(video):
    return video["id"].get("kind") == "youtube#video" and video["snippet"].get("liveBroadcastContent") == "live"

def get_start_time(video_id):
    for api_key in API_KEYS:
        try:
            url = (
                f"https://www.googleapis.com/youtube/v3/videos"
                f"?key={api_key}&id={video_id}&part=liveStreamingDetails"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data["items"][0]["liveStreamingDetails"]["actualStartTime"]
        except Exception as e:
            send_log(f"❌ APIキー `{api_key[:8]}...` での get_start_time に失敗: {e}")
    return None

def convert_to_jst(iso_time):
    utc_time = parser.isoparse(iso_time)
    jst = pytz.timezone("Asia/Tokyo")
    return utc_time.astimezone(jst).strftime('%Y/%m/%d %H:%M:%S')

def send_log(message):
    config = load_config()
    log_channel_id = config.get("log_channel_id")
    logging_enabled = config.get("log_enabled", False)
    if log_channel_id and logging_enabled:
        try:
            from main import bot  # 遅延インポート
            import asyncio
            channel = bot.get_channel(int(log_channel_id))
            if channel:
                asyncio.create_task(channel.send(message))
        except Exception as e:
            print("ログ送信に失敗:", e)

