import hashlib
import hmac
import os

from litestar import Request, Router, post
from litestar.exceptions import HTTPException

import config

route_handlers = []
if config.GITHUB_SECRET:

    async def verify_signature(request: Request):
        signature = (
            "sha256="
            + hmac.new(
                bytes(config.GITHUB_SECRET, "utf-8"),
                msg=await request.body(),
                digestmod=hashlib.sha256,
            ).hexdigest()
        )
        return hmac.compare_digest(signature, request.headers["X-Hub-Signature-256"])

    @post("/reboot", status_code=200, no_auth=True)
    async def github_webhook(request: Request) -> dict[str, str]:
        """The GitHub webhook URL. Runs every time a push is made to the repo."""
        if not await verify_signature(request):
            raise HTTPException(status_code=401, detail="Invalid secret.")
        os.system(
            f"cd {os.getcwd()!r} && git pull && sudo systemctl restart might-be-gay.service"
        )
        return {"status": "ok"}

    route_handlers.append(github_webhook)

router = Router("/private", route_handlers=route_handlers)
