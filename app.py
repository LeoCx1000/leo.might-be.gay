from litestar import Litestar, get
from litestar.response import Redirect


@get("/last.fm-favourite.png")
async def last_fm_favourite() -> Redirect:
    return Redirect(
        "https://img.shields.io/badge/Current Favourite: ないものねだり by KANA--BOON × もっさ-252525?style=flat&logo=spotify"
    )


app = Litestar(route_handlers=[last_fm_favourite])
