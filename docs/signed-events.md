# Signed event receiver utility

`WebhookReceiver` is an optional Agartha.py utility for verifying a separately configured signed HTTP event sender. Native v1 bot commands use the [Gateway](gateway.md). The utility does not register an app endpoint or activate an outbound HTTP interaction/event service.

## Install the optional dependency

Install the wheel with its `webhooks` extra:

```text
python -m pip install "./agartha_py-0.5.0-py3-none-any.whl[webhooks]"
```

This adds the supported PyNaCl dependency. Obtain the approved sender's Ed25519 public key through its configuration process.

## Create a receiver

```python
import os

from aiohttp import web

from agartha import WebhookReceiver


async def received(payload: dict) -> dict:
    return {"accepted": payload["id"]}


if __name__ == "__main__":
    receiver = WebhookReceiver(
        os.environ["AGARTHA_EVENT_PUBLIC_KEY"], received
    )
    web.run_app(
        receiver.create_app(), host="127.0.0.1", port=8081, access_log=None
    )
```

`create_app()` returns an unbound aiohttp application with `POST /events`. The example binds only to loopback. You own production HTTPS hosting, sender registration, access-log policy, and durable receipt handling.

## Verification and receipts

The utility verifies `X-Signature-Ed25519` over the ASCII `X-Signature-Timestamp` followed by the **original raw request body**. The default timestamp tolerance is five minutes. A body must be a JSON object with a stable string delivery `id`; your async handler returns a JSON acknowledgement dictionary.

Duplicate delivery IDs share an in-flight handler or cached acknowledgement. Reusing an ID with different signed content returns HTTP 409. Handler failures/timeouts are retained within the receipt window to avoid blindly repeating uncertain side effects.

Receipt state is bounded and local to the process. Before using production side effects, add durable receipt tracking and make the side effect idempotent across restarts and multiple workers.

## Constructor reference

```text
WebhookReceiver(public_key, handler, *, timestamp_tolerance=300,
                receipt_ttl=900, max_receipts=1000, body_limit=65536,
                handler_timeout=3)
receiver.create_app(*, path="/events") -> aiohttp.web.Application
```

`public_key` is a 32-byte Ed25519 public key encoded as 64 hexadecimal characters. `handler` is an async callable accepting a dictionary and returning a dictionary. Size bounds and timestamps are validated before invoking it. Do not log signature headers, credentials, or the entire body by default.
