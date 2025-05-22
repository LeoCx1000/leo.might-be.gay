from enum import Enum
from typing import Literal, NamedTuple
from jinja2.filters import do_mark_safe


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
    source = Link("https://github.com/leocx1000/leo.might-be.gay", "source")

    # These are for when templating HTML as {{links.home()}} for example:

    def __str__(self):
        return self.value.link

    def __call__(self, mask: str | None = None, **extra: str):
        extra.setdefault("href", self.value.link)
        extra.setdefault("target", self.value.target)
        extra_fmt = " ".join(f"{k}={v!r}" for k, v in extra.items())
        return do_mark_safe(f"<a {extra_fmt}>{mask or self.value[1]}</a>")
