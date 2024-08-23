"""動画情報の収集"""

import time
from datetime import timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import RootModel

from .. import models

VideoList = RootModel[list[models.Video]]

PLAYLISTS = [
    # わしゃがなTV本体
    {
        "id": "UUReBAqqC-hc9d70gOftfitg",
        "delay": timedelta(),
    },
    # 4GamerSP内 / わしゃがなTV（おまけ動画）
    {
        "id": "PLO-B0bLDsrNBmCVuaOmYETDLS9VsXRelq",
        "delay": timedelta(hours=1),
    },
]


def collect_videos(credentials, interval: int = 1) -> VideoList:
    youtube_client = build("youtube", "v3", credentials=credentials)
    items = []
    for idx, playlist in enumerate(PLAYLISTS):
        params = {
            "part": "id,snippet,contentDetails",
            "playlistId": playlist["id"],
            "maxResults": 50,
        }
        cnt = 1
        while True:
            print(f"Call {idx+1}-{cnt}")
            resp = youtube_client.playlistItems().list(**params).execute()
            items += [
                models.Video.model_validate(
                    {
                        "id": item["snippet"]["resourceId"]["videoId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "channel": {
                            "id": item["snippet"]["channelId"],
                            "title": item["snippet"]["channelTitle"],
                        },
                        "thumbnails": {
                            k: models.Thumbnail(
                                size=k,
                                url=v["url"],
                                width=v["width"],
                                height=v["height"],
                            )
                            for k, v in item["snippet"]["thumbnails"].items()
                        },
                        "published_at": item["snippet"]["publishedAt"],
                    }
                )
                for item in resp["items"]
            ]
            next_page_token = resp.get("nextPageToken", None)
            if not next_page_token:
                break
            cnt += 1
            params["pageToken"] = next_page_token
            time.sleep(interval)
    return items


def main():
    credentials = service_account.Credentials.from_service_account_file(
        "service-account.json"
    )
    videos = collect_videos(credentials)
    print(f"{len(videos)} videos")
    Path("videos.json").write_text(VideoList(videos).model_dump_json(indent=2))
