import pathlib
import aiohttp

from litestar import MediaType, Response, get, Router, Request
from litestar.exceptions import HTTPException
from litestar.response import Template
from litestar.controller import Controller
import os

BASE_PATH = pathlib.Path("/www/files")


@get("{filename:path}", media_type=MediaType.HTML)
async def render_code_block(request: Request, filename: str) -> Template:
    file = BASE_PATH / filename.removeprefix("/")

    common = pathlib.Path(os.path.commonprefix([BASE_PATH, file]))

    if common != BASE_PATH or not file.exists() or not file.is_file():
        raise HTTPException(detail="File does not exist.", status_code=404)

    try:
        file.read_text()
    except:
        raise HTTPException(detail="Failed displaying file.", status_code=404)

    session: aiohttp.ClientSession = request.app.state.session
    async with session.get(
        f"http://127.0.0.1:39389/hl",
        params={
            "lang": filename.split(".")[-1],
            "theme": "github-dark",
            "path": file.absolute().as_posix(),
        },
    ) as resp:
        html = await resp.text()

    return Template("code.html", context={"filename": filename, "html": html})


router = Router("code", route_handlers=[render_code_block])
