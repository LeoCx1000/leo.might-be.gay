import asyncio
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Mapping, NamedTuple

import aiohttp
import mistune
from jinja2.filters import do_mark_safe
from litestar import MediaType, Request, Router, get
from litestar.exceptions import HTTPException
from litestar.response import ServerSentEvent, Template, Redirect
from markupsafe import Markup
import random
from urllib.request import urlopen, Request
import config
import requests

REPL = {"and": "&", "_": " "}
PATTERN = re.compile("|".join(re.escape(k) for k in REPL), flags=re.IGNORECASE)
LFM_LOGO = "<img src='/static/graphics/lastfm.svg' style='height:1em; vertical-align:middle; padding-bottom: 0.1em'/>"
GALLERIES_FOLDER = Path("/www/files/gallery")


# Homepage
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


@get("/lastfm-html")
async def serve_lastfm_htmx() -> ServerSentEvent:
    """Updates the real-time music text."""
    if config.LASTFM_API_KEY:
        if not lastfm_poller.waiters:
            asyncio.create_task(lastfm_poller.update_from_lastfm())
        return ServerSentEvent(
            content=lastfm_poller.iterator(), event_type="lastfm-html"
        )
    else:
        return ServerSentEvent(lastfm_poller.NOTHING, event_type="lastfm-html")


@get("/", media_type=MediaType.HTML)
async def home() -> Template:
    return Template(template_name="index.html", context={"age": age()})


@get("/projects", media_type=MediaType.HTML)
async def projects() -> Template:
    return Template(template_name="projects.html")


# Image Galleries
class Image(NamedTuple):
    absolute_url: str
    filename: str


class GalleryFolder(NamedTuple):
    name: str
    readme_html: Markup
    thumbnail: Image | None = None


class CodeBlockRenderer(mistune.HTMLRenderer):
    def block_code(self, code: str, info: str | None = None) -> str:
        url = f"http://127.0.0.1:39389/hltext"
        with requests.post(
            url,
            json=dict(code=code.rstrip(), lang=info or "txt"),
            headers={"Content-Type": "application/json"},
        ) as req:
            return do_mark_safe(req.text)


markdown_renderer = mistune.create_markdown(
    escape=False,
    plugins=["strikethrough", "footnotes", "table", "speedup", "url", "mark"],
    renderer=CodeBlockRenderer(),
)


def render_markdown(markdown: str):
    return do_mark_safe(str(markdown_renderer(markdown)))


def make_readme(folder: Path):
    file = folder / "README.md"
    if not file.exists() or not file.is_file():
        return do_mark_safe("")
    return render_markdown(file.read_text())


def get_images_from_folder(folder: Path, sort: bool = True):
    images = (
        sorted(folder.iterdir(), key=lambda i: i.name, reverse=True)
        if sort
        else folder.iterdir()
    )

    return [
        Image(
            filename=image.name,
            absolute_url=f"/gallery/{folder.name}/{image.name}",
        )
        for image in images
        if image.is_file() and image.name != "README.md"
    ]


@get("/gallery/{folder_name:str}")
async def get_folder(folder_name: str) -> Template:
    folder = GALLERIES_FOLDER / folder_name
    if not (folder_name.isalnum() and folder.exists() and folder.is_dir()):
        raise HTTPException(status_code=404)

    return Template(
        "gallery.html",
        context=dict(
            images=get_images_from_folder(folder),
            folder=GalleryFolder(
                name=folder_name,
                readme_html=make_readme(folder),
            ),
        ),
    )


@get("/gallery", sync_to_thread=True)
def gallery(request: Request) -> Template:
    folders = [
        GalleryFolder(
            name=folder.name,
            readme_html=make_readme(folder),
            thumbnail=random.choice(get_images_from_folder(folder)),
        )
        for folder in sorted(GALLERIES_FOLDER.iterdir(), key=lambda i: i.name)
        if folder.is_dir()
    ]
    return Template("galleries_index.html", context=dict(folders=folders))


# Weblog

WEBLOG_YEARS_DIR = Path("./weblog")
FILE_NAME_RE = re.compile(
    r"^(?P<month>\d{2})-(?P<day>\d{2})(?:-(?P<title>[\w\-]+))?(:?\.md)?$"
)


class File(NamedTuple):
    date: str
    month: str
    day: str
    href: str
    title: str


class WeblogFolder(NamedTuple):
    year: str
    files: list[File]


def get_files_from(folder: Path):
    files: list[File] = []
    for file in sorted(folder.iterdir(), key=lambda f: f.name, reverse=True):
        if not file.is_file():
            continue
        match = FILE_NAME_RE.fullmatch(file.name)
        if not match:
            continue
        year = folder.name
        month = match.group("month")
        day = match.group("day")
        title = match.group("title")
        files.append(
            File(
                date=f"{year}-{month}-{day}",
                title=title.replace("-", " ").title(),
                day=day,
                month=month,
                href=f"/weblog/{year}/{month}-{day}-{title}",
            )
        )
    return files


@get("/weblog", media_type=MediaType.HTML, sync_to_thread=True)
def weblog() -> Template:
    # Scheme: `/Year/Month-Day-title-of-the-log.md`
    folders: list[WeblogFolder] = []
    for folder in sorted(
        WEBLOG_YEARS_DIR.iterdir(), key=lambda dir: dir.name, reverse=True
    ):
        if not folder.is_dir() or not (
            folder.name.isnumeric() and len(folder.name) == 4
        ):
            continue

        files: list[File] = get_files_from(folder)
        if files:
            folders.append(WeblogFolder(year=folder.name, files=files))

    print(folders)
    return Template("weblog_index.html", context=dict(folders=folders))


@get("/weblog/{location:path}")
async def single_weblog(request: Request, location: str) -> Template | Redirect:
    year, sep, file = location.removeprefix("/").partition("/")

    if not year.isdigit() or len(year) != 4:
        raise HTTPException(status_code=404)

    folder = WEBLOG_YEARS_DIR / year
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404)

    if not sep:
        return Template(
            "weblog_index.html",
            context=dict(
                folders=[WeblogFolder(year=year, files=get_files_from(folder))]
            ),
        )

    match = FILE_NAME_RE.fullmatch(file)
    if not match:
        raise HTTPException(status_code=404)

    month = match.group("month")
    day = match.group("day")

    file = folder / (file + ".md")
    if not file.exists():
        file = next(
            filter(
                lambda file: file.name.startswith(f"{month}-{day}"), folder.iterdir()
            ),
            None,
        )
        if not file:
            raise HTTPException(status_code=404)
        return Redirect(f"/weblog/{year}/{file.name.removesuffix('.md')}")

    return Template(
        "weblog.html",
        context={
            "content": render_markdown(file.read_text()),
            "file": File(
                date=f"{year}-{month}-{day}",
                month=month,
                day=day,
                href=str(request.url),  # type: ignore - you do exist don't lie to yourself.
                title=match.group("title").replace("-", " ").title(),
            ),
        },
    )


class NavElement(NamedTuple):
    title: str
    href: str
    current: bool


def navbar(ctx: Mapping[str, Any]) -> list[NavElement]:
    request: Request = ctx["request"]
    return [
        NavElement(
            title=PATTERN.sub(
                lambda m: REPL.get(m.group(0).lower(), m.group(0)),
                route.handler_names[0],
            ).title(),
            href=route.path,
            current=request.url.path == route.path,  # type: ignore
        )
        for route in frontpage.routes
    ]


frontpage = Router("/", route_handlers=[home, projects, weblog, gallery])
backend_hooks = Router("/api", route_handlers=[serve_lastfm_htmx])
router = Router(
    "/", route_handlers=[frontpage, backend_hooks, single_weblog, get_folder]
)
