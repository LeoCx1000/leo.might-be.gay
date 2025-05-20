import pathlib

from litestar import MediaType, Response, get, Router
from litestar.exceptions import HTTPException
from litestar.response import Redirect

BASE_PATH = pathlib.Path("/www/files")


HTML = """
<html>
<head>
    <title>viewing {filename}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/highlightjs-line-numbers.js/2.9.0/highlightjs-line-numbers.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/base16/gigavolt.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/{language}.min.js"></script>
</head>

<style>
body {{
  background-color: #202126;
  color: #ccc;
}}

.hljs-ln-numbers {{
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    text-align: center;
    color: #ccc;
    border-right: 1px solid #CCC;
    vertical-align: top;
    padding-right: 3px !important;
}}

.hljs-ln-line {{
    padding-left: 10px !important;
    color: #ccc;
}}
</style>

<script>hljs.highlightAll();hljs.initLineNumbersOnLoad();</script>

<body><pre><code class="language-{language}">{raw_code}</code></pre></body>
</html>
"""

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


@get("{filename:str}")
async def render_code_block(filename: str) -> Response[str]:
    file = BASE_PATH / filename
    if not file.exists() or not file.is_file() or file.parent != BASE_PATH:
        raise HTTPException(detail="File does not exist.", status_code=404)
    try:
        content = file.read_text()
    except:
        return Redirect(f"/{filename}")
    language = LANGUAGE_MAP.get(file.suffix.removeprefix("."), "plaintext")
    return Response(
        HTML.format(language=language, raw_code=content, filename=filename),
        media_type=MediaType.HTML,
    )


router = Router("code", route_handlers=[render_code_block])
