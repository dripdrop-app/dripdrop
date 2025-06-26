import re
from pathlib import Path
from urllib import parse

import httpx
from fake_useragent import UserAgent
from pydantic import BaseModel

user_agent = UserAgent()


class RetrievedArtwork(BaseModel):
    image: bytes
    extension: str


def is_image_link(response: httpx.Response):
    if content_type := response.headers.get("Content-Type", None):
        if content_type.split("/")[0] == "image":
            return True
    return None


def is_valid_url(url: str):
    u = parse.urlparse(url)
    # Check if scheme(http or https) and netloc(domain) are not empty
    return u[0] != "" and u[1] != ""


def _get_images(response: httpx.Response) -> list:
    html = response.text
    links = set()
    matches = (
        re.findall(r'("[^"]+\.(jpg|png|ico|jpeg)")', html, flags=re.MULTILINE) or []
    )
    for link, _ in matches:
        link = link.replace("\\", "").replace('"', "")
        if not link.startswith("http"):
            link = str(Path(str(response.url)).joinpath(link))
        if is_valid_url(url=link):
            links.add(link)
    return list(links)


async def resolve_artwork(artwork: str):
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=3)
    ) as client:
        response = await client.get(artwork, headers={"User-Agent": user_agent.firefox})
        if response.is_success:
            if is_image_link(response=response):
                return artwork
            img_links = _get_images(response=response)
            if "soundcloud.com" in artwork:
                for img_link in img_links:
                    if "artworks" in img_link and "500x500" in img_link:
                        return img_link
            elif img_links:
                return img_links[0]
        raise Exception("Cannot resolve artwork")


async def retrieve_artwork(artwork_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(artwork_url)
        extension = response.headers.get("Content-Type", "").split("/")[1]
    if not is_image_link(response=response):
        raise None
    return RetrievedArtwork(image=response.content, extension=extension)
