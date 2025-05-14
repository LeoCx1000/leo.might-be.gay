import aiohttp
from typing import TYPE_CHECKING, TypeAlias
from contextlib import asynccontextmanager
from litestar import get, Request, Response, MediaType
from litestar.response import Redirect

from config import LASTFM_API_KEY

LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"

if TYPE_CHECKING:
    from litestar import Litestar as _Litestar

    class Litestar(_Litestar):
        class state:
            session: aiohttp.ClientSession

else:
    from litestar import Litestar

    _Litestar = Litestar


async def request_obsession(app: Litestar | _Litestar, username: str):
    params = {
        "method": "user.getinfo",
        "api_key": LASTFM_API_KEY,
        "user": username,
        "format": "json",
    }
    async with app.state.session.get(LASTFM_API_URL, params=params) as resp:
        return await resp.json()


@get("/last.fm-favourite.png")
async def last_fm_favourite() -> Redirect:
    return Redirect(
        "https://img.shields.io/badge/Current Favourite: ないものねだり by KANA--BOON × もっさ-252525?style=flat&logo=spotify"
    )


@get("/last.fm-favourite")
async def redirect_to_song(request: Request) -> dict:
    return await request_obsession(request.app, "LeoCx1000")


@asynccontextmanager
async def lifespan(app: _Litestar):
    async with aiohttp.ClientSession() as session:
        app.state.session = session
        yield


def handle_404(request: Request, exc: Exception) -> Response:
    if request.url.path.endswith("404.png"):
        return Response("404 not found.")
    return Redirect("/404.png")


app = Litestar(
    route_handlers=[last_fm_favourite, redirect_to_song],
    lifespan=[lifespan],
    exception_handlers={404: handle_404},
)
