import os
import requests
from dateutil import parser
import pytz

API_KEYS = os.getenv("YOUTUBE_API_KEY", "").split(",")

def fetch_latest_video(channel_id):
    errors = []
    for api_key in API_KEYS:
        try:
            url = (
                "https://www.googleapis.com/youtube/v3/search"
                f"?key={api_key}"
                f"&channelId={channel_id}"
                "&part=snippet"
                "&order=date"
                "&maxResults=1"
            )
            response = requests.get(url)
            data = response.json()

            if "error" in data:
                error_reason = data["error"]["errors"][0].get("reason", "unknown")
                errors.append((api_key, error_reason))
                continue

            items = data.get("items")
            if items:
                return items[0]
        except Exception as e:
            errors.append((api_key, str(e)))
            continue

    raise Exception(f"全APIキーでの動画取得に失敗しました: {errors}")

def is_livestream(video):
    return video["snippet"].get("liveBroadcastContent") == "live"

def get_start_time(video):
    published_at = video["snippet"]["publishedAt"]
    dt = parser.isoparse(published_at).astimezone(pytz.timezone("Asia/Tokyo"))
    return dt.strftime("%Y年%m月%d日 %H:%M:%S")

async def log_to_channel(bot, log_channel_id, message):
    try:
        channel = bot.get_channel(int(log_channel_id))
        if channel:
            await channel.send(f"📛 **ログ**: {message}")
    except Exception as e:
        print(f"ログチャンネルへの送信に失敗しました: {e}")

