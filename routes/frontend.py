import asyncio
import re
from datetime import date
from typing import Any, Mapping

import aiohttp
from litestar import MediaType, Request, Router, get
from litestar.response import ServerSentEvent, Template
from litestar.plugins.htmx import HTMXTemplate

import config

REPL = {"and": "&", "_": " "}
PATTERN = re.compile("|".join(re.escape(k) for k in REPL), flags=re.IGNORECASE)
LFM_LOGO = "<img src='/static/graphics/lastfm.svg' style='height:1em; vertical-align:middle; padding-bottom: 0.1em'/>"


class LastFmPoller:
    NOTHING = f"<p>{LFM_LOGO} Listening to <i>nothing rn...</i></p>"
    LISTENING_TO = "<p>{LFM_LOGO} Listening to <a href={song_url} target='_blank'><b>{song}</b></a> by {artist}</p>"
    LAST_LISTENED = "<p>{LFM_LOGO} Last listened to <a href={song_url} target='_blank'><b>{song}</b></a> by {artist}</p>"

    def __init__(self):
        self.waiters: dict[int, asyncio.Event] = {}
        self.html = self.NOTHING
        asyncio.create_task(self.lastfm_getter())

    def set_waiters(self):
        for waiter in self.waiters.values():
            waiter.set()

    async def update_from_lastfm(self, session: aiohttp.ClientSession | None = None):
        _session = session or aiohttp.ClientSession()
        try:
            params = {
                "method": "user.getrecenttracks",
                "user": config.LASTFM_USERNAME,
                "format": "json",
                "api_key": config.LASTFM_API_KEY,
                "limit": 1,
            }
            async with _session.get(
                "http://ws.audioscrobbler.com/2.0/", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        song = data["recenttracks"]["track"][0]
                        song_name = song["name"]
                        song_url = song["url"]
                        song_artist = song["artist"]["#text"]

                        if song.get("@attr", {}).get("nowplaying") == "true":
                            to_fmt = self.LISTENING_TO
                        else:
                            to_fmt = self.LAST_LISTENED

                        new_html = to_fmt.format(
                            LFM_LOGO=LFM_LOGO,
                            song_url=song_url,
                            song=song_name,
                            artist=song_artist,
                        )
                        if self.html != new_html:
                            self.html = new_html
                            self.set_waiters()

                    except (KeyError, AssertionError):
                        if self.html != self.NOTHING:
                            self.html = self.NOTHING
                            self.set_waiters()
        finally:
            if not session:
                await _session.close()

    async def lastfm_getter(self):
        async with aiohttp.ClientSession() as session:
            while True:
                if self.waiters:
                    await self.update_from_lastfm(session)
                await asyncio.sleep(2)

    async def iterator(self):
        yield self.html
        waiter = asyncio.Event()
        self.waiters[id(waiter)] = waiter
        try:
            while True:
                await waiter.wait()
                yield self.html
                waiter.clear()
        finally:
            self.waiters.pop(id(waiter))


def age():
    born, today = date(2003, 9, 5), date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@get("/", media_type=MediaType.HTML)
async def home_and_about(request: Request) -> Template:
    return Template(template_name="index.html", context={"age": age()})


@get("/projects", media_type=MediaType.HTML)
async def my_projects(request: Request) -> Template:
    return Template(template_name="projects.html")


lastfm_poller = LastFmPoller()


@get("/lastfm-html")
async def serve_lastfm_htmx() -> ServerSentEvent:
    if config.LASTFM_API_KEY:
        if not lastfm_poller.waiters:
            asyncio.create_task(lastfm_poller.update_from_lastfm())
        return ServerSentEvent(
            content=lastfm_poller.iterator(), event_type="lastfm-html"
        )
    else:
        return ServerSentEvent(lastfm_poller.NOTHING, event_type="lastfm-html")


def navbar(ctx: Mapping[str, Any]) -> str:
    request: Request = ctx["request"]

    fmt: list[str] = []
    for route in frontpage.routes:
        extra = f' class="nav-current"' if request.url.path == route.path else f""
        name = PATTERN.sub(
            lambda m: REPL.get(m.group(0).lower(), m.group(0)), route.handler_names[0]
        ).title()
        fmt.append(f'<a href="{route.path}"{extra}>{name}</a>')
    return "\n".join(fmt)


frontpage = Router("/", route_handlers=[home_and_about, my_projects])
backend_hooks = Router("/api", route_handlers=[serve_lastfm_htmx])
router = Router("/", route_handlers=[frontpage, backend_hooks])
