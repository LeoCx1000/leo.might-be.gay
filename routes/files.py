import pathlib
import aiohttp

from litestar import MediaType, Response, get, Router, Request
from litestar.exceptions import HTTPException
from litestar.response import Template

BASE_PATH = pathlib.Path("/www/files")


LANGUAGE_MAP = {
    # I could set it to auto... nah!
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "txt": "plaintext",
    "log": "plaintext",
    "md": "markdown",
    "toml": "ini",
    "yaml": "yaml",
    "json": "json",
    "css": "css",
}


@get("{filename:str}", media_type=MediaType.HTML)
async def render_code_block(request: Request, filename: str) -> Template:
    file = BASE_PATH / filename
    if not file.exists() or not file.is_file() or file.parent != BASE_PATH:
        raise HTTPException(detail="File does not exist.", status_code=404)

    try:
        content = file.read_text()
    except:
        raise HTTPException(detail="Failed displaying file.", status_code=404)

    session: aiohttp.ClientSession = request.app.state.session
    async with session.get(
        f"http://127.0.0.1:39389/hl/{filename}",
        params={"lang": filename.split(".")[-1], "theme": "github-dark"},
    ) as resp:
        html = await resp.text()

    return Template("code.html", context={"filename": filename, "html": html})


router = Router("code", route_handlers=[render_code_block])
