# Errors and rate limits

Agartha.py schedules API calls and raises specific exceptions when a request cannot complete. Keep one quota strategy across your bot workers and handle permission changes as normal application behavior.

## Handle API errors

```python
from agartha import AuthenticationError, Forbidden, NotFound, RateLimited, TransportError


async def post_update(client, channel_id: str) -> str:
    try:
        message = await client.create_message(
            channel_id, content="Update ready.", nonce="update-operation-42"
        )
        return message.id
    except AuthenticationError:
        raise  # Stop this client and replace its credentials.
    except Forbidden:
        return "The bot needs permission in this channel."
    except NotFound:
        return "The channel is no longer available."
    except RateLimited as error:
        return f"Busy; try again after {error.retry_after:.1f} seconds."
    except TransportError:
        return "Delivery is unconfirmed; reconcile this operation before repeating it."
```

Every exported SDK exception derives from `AgarthaError`. HTTP-related exceptions expose `.status` without including the response body or credentials in their text.

| Exception | Meaning |
| --- | --- |
| `AuthenticationError` | HTTP 401 or invalid Gateway credentials; this Client stops further requests |
| `Forbidden` | HTTP 403; application lacks current permission or approved access |
| `NotFound` | HTTP 404; resource unavailable or outside current visibility |
| `RateLimited` | HTTP 429 retry budget exhausted; `.retry_after` is seconds |
| `HTTPError` | Other unsuccessful HTTP status; inspect `.status` |
| `TransportError` | Connection/timeout failure with uncertain request delivery |
| `ProtocolError` | Invalid response shape or unsupported protocol data |
| `InteractionExpired` | Initial response or follow-up deadline elapsed |
| `GatewayError` | Gateway failure; `.code` identifies a terminal close when available |
| `OAuthError` | OAuth failure; `.status` and recognized `.error` code |

Invalid local arguments can raise `ValueError` or `TypeError`. A second initial response can raise `RuntimeError`.

## REST scheduling

The SDK learns buckets from `X-RateLimit-Bucket`, `X-RateLimit-Remaining`, and reset headers. It separates major server/channel resources, waits for route deadlines, and observes global 429 responses. Normal requests share a **50 requests/second** application limit. Callback and follow-up routes use their own buckets.

Current default route policies include:

| Route family | Current limit |
| --- | --- |
| Most metadata reads | 10 per 5 seconds |
| Channel/message/role/moderation/reaction families | 5 per 5 seconds |
| Command replacement | 2 per 5 seconds |
| Interaction callback and follow-up family | 10 per second |
| Normal application requests | 50 per second globally |

The response headers and returned retry deadline are authoritative. Do not assume every route has a permanent fixed allowance or create more clients to multiply the application's quota. Bucket scheduling in the SDK is process-local; distributed workers need coordinated queues or a shared limiter.

## Retry behavior

`Client(..., max_retries=3)` retries only confirmed HTTP 429 responses, after the required delay. It does not automatically replay connection failures, other unsuccessful statuses, or malformed success responses.

A timed-out mutation may already have succeeded. Reconcile before retrying. For message creation, reuse the same stable nonce **and identical payload** for that operation. A different payload under the same nonce is a conflict. Other mutations do not gain general idempotency from a nonce.

An HTTP 401 invalidates the client. Rotate or restore the correct token, then construct a new Client/Bot. Continually retrying an expired credential does not restore authority.

OAuth exchanges and refreshes are never automatically repeated, including after a 429. Refresh rotation may have already consumed the old token. Coordinate refreshes for the same user grant and persist the replacement token pair together.

## Interaction and Gateway limits

| Operation | Limit |
| --- | --- |
| Initial interaction acknowledgement | 3 seconds |
| Follow-up response token | 15 minutes |
| Outgoing Gateway frames | 120 per connection per 60 seconds |
| Outgoing Gateway frame size | 4,096 UTF-8 bytes |
| Presence updates | 5 per 20 seconds |
| Identify concurrency bucket | One start per 5 seconds; use discovery's concurrency/start budget |
| Native retained session/events | 15 minutes |

Defer a command before slow work. For component updates use `defer_update`; for a long new reply use `defer`. Autocomplete must return its choice response directly and cannot defer.

## Diagnose common failures

| Symptom | Check |
| --- | --- |
| Developer panel remains pending | Staff admission approval; MFA alone does not approve an application |
| Sensitive panel action asks for verification | Complete two-factor verification in the current session |
| Command absent | App installed, definitions synced in intended scope, current user/channel permitted |
| Command handler not called | Running Gateway, matching command/path/custom ID, accepted intents |
| Member list forbidden | Members intent approved, server installation visible |
| Human message body empty | Message-content approval and current visibility |
| Bot cannot change a role/member | Installation grant, current permission, managed-role hierarchy |
| Form/menu rejected | Replaced or expired source, changed channel/user, lost permission, or reused submission |
| Attachment unavailable | Submitted interaction ownership, current permission, expiry, MIME/size limits |
| Provider alert absent | Subscription enabled, quiet baseline, scheduler/provider availability |
| Product checkout unavailable | Monetization approval, beneficiary verification, and platform activation |

When asking support for help, provide the app/server/channel IDs, UTC time, SDK version, and a concise recognized status/error. Keep tokens, interaction URLs, OAuth secrets, and customer payment details out of logs and support messages.
