import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

import aiohttp
from litestar import Litestar, Request, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import HTTPException
from litestar.plugins.htmx import HTMXPlugin
from litestar.response import Redirect, Template
from litestar.static_files import StaticFilesConfig
from litestar.template.config import TemplateConfig

from routes import files, frontend, music_badges, private
from utils.links import Links


def register_engine_callables(engine: JinjaTemplateEngine):
    engine.register_template_callable("navbar", frontend.navbar)

    engine.engine.globals.update(dict(links=Links))


def handle_exception(request: Request, exc: HTTPException) -> Template:
    return Template("error_code.html", context=dict(error=str(exc)))


@asynccontextmanager
async def lifespan(app: Litestar):
    async with aiohttp.ClientSession() as session:
        app.state.session = session
        p = subprocess.Popen(["node", "utils/shiki.js"])
        yield
        p.terminate()


app = Litestar(
    route_handlers=[
        music_badges.router,
        files.router,
        frontend.router,
        private.router,
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
