import os
import requests
from datetime import datetime
from dateutil import parser
import pytz
import random

from utils.config import load_config

# 複数APIキーの読み込み
YOUTUBE_API_KEYS = os.getenv("YOUTUBE_API_KEY", "").split(",")

# JST変換
def convert_to_jst(datetime_str):
    dt = parser.parse(datetime_str)
    utc = pytz.utc.localize(dt)
    jst = utc.astimezone(pytz.timezone('Asia/Tokyo'))
    return jst.strftime("%Y/%m/%d %H:%M:%S")

# ライブ配信かどうか
def is_livestream(video_data):
    return video_data["snippet"].get("liveBroadcastContent") == "live"

# ライブ開始時刻取得
def get_start_time(video_data):
    live_details = video_data.get("liveStreamingDetails")
    if live_details and "actualStartTime" in live_details:
        return convert_to_jst(live_details["actualStartTime"])
    return None

# ログチャンネルにエラー通知
async def notify_log_channel(bot, guild_id: str, message: str):
    config = load_config()
    guild_config = config.get(guild_id)
    if guild_config:
        log_channel_id = guild_config.get("log_channel_id")
        if log_channel_id:
            channel = bot.get_channel(int(log_channel_id))
            if channel:
                await channel.send(f"📛 **YouTube API エラー通知**\n{message}")

# APIキーを使ってリクエスト、失敗したら次のキーでリトライ
def get_valid_response(url):
    for api_key in YOUTUBE_API_KEYS:
        full_url = f"{url}&key={api_key}"
        res = requests.get(full_url)
        if res.status_code == 200:
            return res.json()
        # クォータエラー等があればスキップ
        try:
            error_msg = res.json().get("error", {}).get("message", "").lower()
            if "quota" in error_msg or "key" in error_msg:
                continue
        except Exception:
            continue
    return None

# 最新動画の取得
async def fetch_latest_video(bot, channel_id: str, guild_id: str):
    base_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
    )
    data = get_valid_response(base_url)
    if not data:
        await notify_log_channel(bot, guild_id, f"❌ 最新動画の取得に失敗しました。チャンネルID: `{channel_id}`")
        return None

    items = data.get("items")
    if not items:
        return None
    return items[0]

# 動画の詳細取得（startTimeなど）
async def fetch_video_details(bot, video_id: str, guild_id: str):
    base_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?id={video_id}&part=snippet,liveStreamingDetails"
    )
    data = get_valid_response(base_url)
    if not data:
        await notify_log_channel(bot, guild_id, f"❌ 動画詳細の取得に失敗しました。Video ID: `{video_id}`")
        return None

    items = data.get("items")
    if not items:
        return None
    return items[0]

# 過去動画を取得
async def fetch_all_videos(bot, channel_id: str, guild_id: str, max_results=10):
    base_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?channelId={channel_id}&part=snippet,id&order=date&maxResults={max_results}"
    )
    data = get_valid_response(base_url)
    if not data:
        await notify_log_channel(bot, guild_id, f"❌ 過去動画の取得に失敗しました。チャンネルID: `{channel_id}`")
        return None

    return data.get("items", [])
