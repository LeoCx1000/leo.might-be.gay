import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

import aiohttp
from litestar import Litestar, Request, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import HTTPException
from litestar.plugins.htmx import HTMXPlugin
from litestar.response import Template
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

from routes import files, frontend, music_badges, private
from utils.links import Links
from urllib.parse import quote_plus


def register_engine_callables(engine: JinjaTemplateEngine):
    engine.register_template_callable("navbar", frontend.navbar)

    engine.engine.globals.update(links=Links)
    engine.engine.filters.update(quote=lambda s: quote_plus(s))


def handle_exception(request: Request, exc: HTTPException) -> Template:
    return Template(
        "error_code.html",
        context=dict(error=str(exc)),
        status_code=exc.status_code,
    )


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
        create_static_files_router(path="static", directories=[Path("static")]),
    ],
    lifespan=[lifespan],
    exception_handlers={HTTPException: handle_exception},
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
        engine_callback=register_engine_callables,
    ),
    plugins=[HTMXPlugin()],
    openapi_config=None,
)
