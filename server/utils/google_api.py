import logging
import requests
from typing import List
from urllib import parse
from server.config import config

scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
    "https://www.googleapis.com/auth/youtube.readonly",
]

base_headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/51.0.2704.103 Safari/537.36"
    )
}

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


def create_oauth_url(callback_url: str, user_id: str):
    if config.env == "production":
        callback_url = callback_url.replace("http", "https", count=1)
    params = {
        "client_id": config.google_client_id,
        "redirect_uri": callback_url,
        "scope": " ".join(scopes),
        "response_type": "code",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": user_id,
    }
    return {
        "params": params,
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?{parse.urlencode(params)}",
    }


def get_oauth_tokens(callback_url: str, code: str):
    if config.env == "production":
        callback_url = callback_url.replace("http", "https", count=1)
    params = {
        "code": code,
        "client_id": config.google_client_id,
        "client_secret": config.google_client_secret,
        "redirect_uri": callback_url,
        "grant_type": "authorization_code",
    }
    response = requests.post(
        "https://oauth2.googleapis.com/token", data=params, headers=base_headers
    )
    if response.ok:
        return response.json()
    logging.warning(response.text)
    return None


def refresh_access_token(refresh_token: str):
    params = {
        "client_id": config.google_client_id,
        "client_secret": config.google_client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(
        "https://oauth2.googleapis.com/token", params=params, headers=base_headers
    )
    if response.ok:
        return response.json()
    logging.warning(response.text)
    return None


def get_user_email(access_token: str):
    params = {"fields": "email"}
    headers = {"Authorization": f"Bearer {access_token}", **base_headers}
    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers, params=params
    )
    if response.ok:
        json = response.json()
        return json.get("email")
    logging.warning(response.text)
    return None


def get_video_categories():
    params = {"key": config.google_api_key, "part": "snippet", "regionCode": "US"}
    response = requests.get(
        f"{YOUTUBE_API_URL}/videoCategories",
        params=params,
        headers=base_headers,
    )
    if response.ok:
        json = response.json()
        return json.get("items", [])
    logging.warning(response.text)
    return []


def get_user_subscriptions(access_token: str):
    params = {
        "part": "snippet",
        "mine": True,
        "maxResults": 50,
        "pageToken": "",
    }
    headers = {"Authorization": f"Bearer {access_token}", **base_headers}
    while params.get("pageToken") is not None:
        response = requests.get(
            f"{YOUTUBE_API_URL}/subscriptions",
            params=params,
            headers=headers,
        )
        if response.ok:
            json = response.json()
            yield json.get("items")
            params["pageToken"] = json.get("nextPageToken", None)
        else:
            logging.warning(response.text)
            yield []
            params["pageToken"] = None


def get_channels_info(channel_ids: List[str]):
    params = {
        "key": config.google_api_key,
        "part": "snippet,contentDetails",
        "id": ",".join(channel_ids),
        "maxResults": 50,
    }
    response = requests.get(
        f"{YOUTUBE_API_URL}/channels",
        params=params,
        headers=base_headers,
    )
    if response.ok:
        json = response.json()
        return json.get("items", [])
    logging.warning(response.text)
    return []


def get_playlist_videos(playlist_id: str):
    params = {
        "key": config.google_api_key,
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "pageToken": "",
    }
    while params.get("pageToken") is not None:
        response = requests.get(
            f"{YOUTUBE_API_URL}/playlistItems",
            params=params,
            headers=base_headers,
        )
        if response.ok:
            json = response.json()
            yield json.get("items", [])
            params["pageToken"] = json.get("nextPageToken", None)
        else:
            logging.warning(response.text)
            yield []
            params["pageToken"] = None


def get_videos_info(video_ids: str):
    params = {
        "key": config.google_api_key,
        "part": "snippet",
        "id": ",".join(video_ids),
        "maxResults": 50,
    }
    response = requests.get(f"{YOUTUBE_API_URL}/videos", params=params)
    if response.ok:
        json = response.json()
        return json.get("items", [])
    logging.warning(response.text)
    return []
