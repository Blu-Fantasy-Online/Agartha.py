"""Optional receiver utility demonstration; no native delivery registration occurs."""

import os
from typing import Any

from aiohttp import web

from agartha import WebhookReceiver


async def received(payload: dict[str, Any]) -> dict[str, Any]:
    # Add a durable receipt and idempotent application transaction before using
    # this handler for production side effects.
    return {"accepted": payload["id"]}


if __name__ == "__main__":
    receiver = WebhookReceiver(os.environ["AGARTHA_EVENT_PUBLIC_KEY"], received)
    web.run_app(receiver.create_app(), host="127.0.0.1", port=8081, access_log=None)
