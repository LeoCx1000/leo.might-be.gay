import re
from litestar import get, Request, MediaType, Router
from litestar.response import Template
from typing import Mapping, Any

from datetime import date

REPL = {"and": "&", "_": " "}
PATTERN = re.compile("|".join(re.escape(k) for k in REPL), flags=re.IGNORECASE)


def age():
    born, today = date(2003, 9, 5), date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@get("/home", media_type=MediaType.HTML)
async def home_and_about(request: Request) -> Template:
    return Template(template_name="index.html", context={"age": age()})


@get("/projects", media_type=MediaType.HTML)
async def my_projects(request: Request) -> Template:
    return Template(template_name="projects.html")


router = Router("/", route_handlers=[home_and_about, my_projects])


def navbar(ctx: Mapping[str, Any]) -> str:
    request: Request = ctx["request"]
    fmt: list[str] = []
    for route in router.routes:
        extra = f' class="nav-current"' if request.url.path == route.path else f""
        name = PATTERN.sub(
            lambda m: REPL.get(m.group(0).lower(), m.group(0)), route.handler_names[0]
        ).title()
        fmt.append(f'<a href="{route.path}"{extra}>{name}</a>')
    return "\n".join(fmt)
