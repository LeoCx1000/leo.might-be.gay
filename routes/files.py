import pathlib
import aiohttp

from litestar import MediaType, get, Router, Request
from litestar.exceptions import HTTPException
from litestar.response import Template
import os
from .frontend import render_markdown

BASE_PATH = pathlib.Path("/www/files")


def get_file(filename: str):
    file = BASE_PATH / filename.removeprefix("/")

    common = pathlib.Path(os.path.commonprefix([BASE_PATH, file.resolve()]))

    if common != BASE_PATH or not file.exists() or not file.is_file():
        raise HTTPException(detail="File does not exist", status_code=404)
    try:
        return (file, file.read_text())
    except Exception as e:
        raise HTTPException(detail=f"Failed displaying file. {e}", status_code=404)


@get("code/{filename:path}", media_type=MediaType.HTML)
async def render_code_block(request: Request, filename: str) -> Template:
    file, _ = get_file(filename)

    session: aiohttp.ClientSession = request.app.state.session
    async with session.get(
        "http://127.0.0.1:39389/hl",
        params={
            "lang": filename.split(".")[-1],
            "theme": "github-dark",
            "path": file.absolute().as_posix(),
        },
    ) as resp:
        html = await resp.text()

    return Template("code.html", context={"filename": filename, "html": html})


@get("md/{filename:path}")
async def render_md_file(filename: str) -> Template:
    print("file")
    if not filename.endswith("md"):
        raise HTTPException("Can only render MakDown files.")
    _, contents = get_file(filename)

    return Template(
        "markdown.html",
        context={"content": render_markdown(contents), "title": filename},
    )


router = Router("", route_handlers=[render_code_block, render_md_file])
