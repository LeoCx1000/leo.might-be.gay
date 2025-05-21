from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Mapping, NamedTuple, Literal

import aiohttp
from litestar import Litestar, MediaType, Request, get
from litestar.exceptions import HTTPException
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Redirect, Template
from litestar.static_files import StaticFilesConfig
from litestar.template.config import TemplateConfig
import subprocess
from routes import files, frontend, music_badges, private

from enum import Enum
from jinja2.filters import do_mark_safe


class Link(NamedTuple):
    link: str
    label: str
    target: Literal["_blank", "_parent", "_self", "_top"] = "_blank"


class Links(Enum):
    home = Link("/", "home", target="_self")
    discord = Link("https://discord.gg/TdRfGKg8Wh", "discord")
    github = Link("https://github.com/LeoCx1000", "github")
    anilist = Link("https://anilist.co/user/LeoCx1000", "anilist")
    mal = Link("https://myanimelist.net/animelist/LeoCx1000", "MAL")
    lastfm = Link("https://last.fm/user/LeoCx1000", "last.fm")
    steam = Link("https://steamcommunity.com/profiles/76561198971611430", "steam")
    reddit = Link("https://www.reddit.com/user/LeoCx1000/", "reddit")
    jinja2 = Link("https://jinja.palletsprojects.com/", "jinja2")
    litestar = Link("https://litestar.dev/", "litestar")
    dpy = Link("https://pypi.org/project/discord.py/", "discord.py")
    dpy_inv = Link("https://discord.gg/dpy", "discord.py server")

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
    openapi_config=None,
)
