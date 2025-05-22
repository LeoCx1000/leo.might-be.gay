import asyncio
import re
from datetime import date
from pathlib import Path
from typing import Any, Mapping, NamedTuple

import aiohttp
import mistune
from jinja2.filters import do_mark_safe
from litestar import MediaType, Request, Router, get
from litestar.exceptions import HTTPException
from litestar.response import ServerSentEvent, Template
from markupsafe import Markup

import config

REPL = {"and": "&", "_": " "}
PATTERN = re.compile("|".join(re.escape(k) for k in REPL), flags=re.IGNORECASE)
LFM_LOGO = "<img src='/static/graphics/lastfm.svg' style='height:1em; vertical-align:middle; padding-bottom: 0.1em'/>"
GALLERIES_FOLDER = Path("/www/files/galleries")


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


lastfm_poller = LastFmPoller()


def age():
    born, today = date(2003, 9, 5), date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@get("/", media_type=MediaType.HTML)
async def home_and_about(request: Request) -> Template:
    return Template(template_name="index.html", context={"age": age()})


@get("/projects", media_type=MediaType.HTML)
async def projects(request: Request) -> Template:
    return Template(template_name="projects.html")


class Folder(NamedTuple):
    name: str
    readme_html: Markup


class Image(NamedTuple):
    absolute_url: str
    filename: str


def make_readme(folder: Path):
    file = folder / "README.md"
    if not file.exists() or not file.is_file():
        return do_mark_safe("")
    return do_mark_safe(str(mistune.html(file.read_text())))


@get("/gallery/{folder_name:str}")
async def get_folder(folder_name: str) -> Template:
    folder = GALLERIES_FOLDER / folder_name
    if not (folder_name.isalnum() and folder.exists() and folder.is_dir()):
        raise HTTPException(status_code=404)

    images = [
        Image(
            filename=image.name,
            absolute_url=f"/gallery/{folder_name}/{image.name}",
        )
        for image in sorted(folder.iterdir(), key=lambda i: i.name, reverse=True)
        if image.is_file() and image.name != "README.md"
    ]

    return Template(
        "gallery.html",
        context=dict(
            images=images,
            folder=Folder(
                name=folder_name,
                readme_html=make_readme(folder),
            ),
        ),
    )


@get("/gallery", sync_to_thread=True)
def gallery(request: Request) -> Template:
    folders = [
        Folder(name=folder.name, readme_html=make_readme(folder))
        for folder in sorted(
            GALLERIES_FOLDER.iterdir(), key=lambda i: i.name, reverse=True
        )
        if folder.is_dir()
    ]
    return Template("galleries_index.html", context=dict(folders=folders))


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


frontpage = Router("/", route_handlers=[home_and_about, projects, gallery])
backend_hooks = Router("/api", route_handlers=[serve_lastfm_htmx])
router = Router("/", route_handlers=[frontpage, backend_hooks, get_folder])
