import subprocess
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Literal, NamedTuple

import aiohttp
from jinja2.filters import do_mark_safe
from litestar import Litestar, Request, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import HTTPException
from litestar.plugins.htmx import HTMXPlugin
from litestar.response import Redirect, Template
from litestar.static_files import StaticFilesConfig
from litestar.template.config import TemplateConfig

from routes import files, frontend, music_badges, private


class Link(NamedTuple):
    link: str
    label: str
    target: Literal["_blank", "_parent", "_self", "_top"] = "_blank"


class Links(Enum):
    home = Link("/", "home", target="_self")
    discord = Link("https://discord.gg/TdRfGKg8Wh", "Discord")
    github = Link("https://github.com/LeoCx1000", "GitHub")
    anilist = Link("https://anilist.co/user/LeoCx1000", "AniList")
    mal = Link("https://myanimelist.net/animelist/LeoCx1000", "MAL")
    lastfm = Link("https://last.fm/user/LeoCx1000", "last.fm")
    steam = Link("https://steamcommunity.com/profiles/76561198971611430", "Steam")
    reddit = Link("https://www.reddit.com/user/LeoCx1000/", "reddit")
    jinja2 = Link("https://jinja.palletsprojects.com/", "jinja2")
    litestar = Link("https://litestar.dev/", "litestar")
    dpy = Link("https://pypi.org/project/discord.py/", "discord.py")
    dpy_inv = Link("https://discord.gg/dpy", "discord.py server")
    arduino = Link("https://arduino.cc/", "Arduino")
    godot = Link("https://godotengine.org/", "Godot")
    python = Link("https://www.python.org/", "Python")

    def __str__(self):
        return self.value.link

    def __call__(self, mask: str | None = None, **extra: str):
        extra.setdefault("href", self.value.link)
        extra.setdefault("target", self.value.target)
        extra_fmt = " ".join(f"{k}={v!r}" for k, v in extra.items())
        return do_mark_safe(f"<a {extra_fmt}>{mask or self.value[1]}</a>")


def register_engine_callables(engine: JinjaTemplateEngine):
    engine.register_template_callable("navbar", frontend.navbar)

    engine.engine.globals.update(dict(links=Links))


@get("/favicon.ico")
async def favicon() -> Redirect:
    return Redirect("/static/graphics/favicon.ico")


def handle_exception(request: Request, exc: HTTPException) -> Template:
    return Template("error_code.html", context=dict(error=str(exc)))


@asynccontextmanager
async def lifespan(app: Litestar):
    async with aiohttp.ClientSession() as session:
        app.state.session = session
        p = subprocess.Popen(["node", "shiki.js"])
        yield
        p.terminate()


app = Litestar(
    route_handlers=[
        music_badges.router,
        files.router,
        frontend.router,
        private.router,
        favicon,
    ],
    lifespan=[lifespan],
    exception_handlers={HTTPException: handle_exception},
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
        engine_callback=register_engine_callables,
    ),
    static_files_config=[
        StaticFilesConfig(path="static", directories=[Path("static")])
    ],
    plugins=[HTMXPlugin()],
    openapi_config=None,
)
