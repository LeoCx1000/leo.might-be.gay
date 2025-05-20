import urllib.parse

from litestar import Litestar, MediaType, Request, Response, get, Router
from litestar.response import Redirect

OPEN_URL = "https://open.spotify.com/track/{0}"
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"


async def request_obsession(app: Litestar, user_id: int):
    async with app.state.session.get(
        f"http://localhost:8716/obsession/{user_id}"
    ) as resp:
        return resp.status, await resp.json()


async def request_playing(app: Litestar, user_id: int):
    async with app.state.session.get(
        f"http://localhost:8716/spotify/{user_id}"
    ) as resp:
        return resp.status, await resp.json()


def badge_quote(string: str) -> str:
    return urllib.parse.quote(string).replace("-", "--").replace("_", "__")


@get("/obsession/{user_id:int}/image")
async def last_fm_favourite(request: Request, user_id: int) -> Redirect:
    status, obsession = await request_obsession(request.app, user_id)

    if status == 404:
        return Redirect(
            "https://img.shields.io/badge/No obsession set.-252525?style=flat&logo=spotify"
        )
    track_name = obsession["title"]
    artist = obsession["artist"]
    request.url
    return Redirect(
        f"https://img.shields.io/badge/Current_Favourite: {badge_quote(track_name)} by {badge_quote(artist)}-252525?style=flat&logo=spotify"
    )


@get("/obsession/{user_id:int}/redirect")
async def redirect_to_song(request: Request, user_id: int) -> Response:
    status, obsession = await request_obsession(request.app, user_id)
    if status == 404:
        return Response(
            'Obsession not set. Please join our discord server and use the "/obsession set" command. https://discord.gg/TdRfGKg8Wh',
            media_type=MediaType.TEXT,
        )
    return Redirect(OPEN_URL.format(obsession["track_id"]))


@get("/listening/{user_id:int}/image")
async def currently_playing(request: Request, user_id: int) -> Redirect:
    status, obsession = await request_playing(request.app, user_id)

    if status == 404:
        return Redirect(
            "https://img.shields.io/badge/Not listening to anything-252525?style=flat&logo=spotify"
        )
    track_name = obsession["title"]
    artist = obsession["artist"]
    return Redirect(
        f"https://img.shields.io/badge/Listening to {badge_quote(track_name)} by {badge_quote(artist)}-252525?style=flat&logo=spotify"
    )


@get("/listening/{user_id:int}/redirect")
async def redirect_to_playing(request: Request, user_id: int) -> Response:
    status, obsession = await request_playing(request.app, user_id)
    if status == 404:
        return Response(
            "Please join our discord server so our bot can see your Discord Spotify activity. https://discord.gg/TdRfGKg8Wh",
            media_type=MediaType.TEXT,
        )
    return Redirect(OPEN_URL.format(obsession["track_id"]))


router = Router(
    "/",
    route_handlers=[
        last_fm_favourite,
        redirect_to_song,
        currently_playing,
        redirect_to_playing,
    ],
)
