"""動画情報の収集"""
import json
import time
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

PLAYLISTS = [
    "UUReBAqqC-hc9d70gOftfitg",  # わしゃがなTV本体
    "PLO-B0bLDsrNBmCVuaOmYETDLS9VsXRelq",  # 4GamerSP内 / わしゃがなTV（おまけ動画）
]


def collect_videos(credentials, interval: int = 1):
    youtube_client = build("youtube", "v3", credentials=credentials)
    items = []
    for idx, playlist_id in enumerate(PLAYLISTS):
        params = {
            "part": "id,snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
        }
        cnt = 1
        while True:
            print(f"Call {idx+1}-{cnt}")
            resp = youtube_client.playlistItems().list(**params).execute()
            items += resp["items"]
            next_page_token = resp.get("nextPageToken", None)
            if not next_page_token:
                break
            cnt += 1
            params["pageToken"] = next_page_token
            time.sleep(interval)
    return items


def main():
    credentials = service_account.Credentials.from_service_account_file("service-account.json")
    videos = collect_videos(credentials)
    print(f"{len(videos)} videos")
    Path("videos.json").write_text(json.dumps(videos, ensure_ascii=False, indent=2))
