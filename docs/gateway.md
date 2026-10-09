# Gateway and events

The Gateway is the persistent event connection for your application. `Bot` starts it for you. Agartha.py discovers the connection address, identifies, maintains heartbeats, and resumes after eligible disconnects.

## Register event handlers

```python
from agartha import Message


@bot.event
async def on_ready(payload: dict) -> None:
    print("Connected")


@bot.event
async def on_message(message: Message) -> None:
    print("Visible message event received")


@bot.event
async def on_message_delete(payload: dict) -> None:
    print("Message removed")


@bot.event
async def on_error(event_name: str, error: Exception) -> None:
    print(f"Handler failed: {event_name} ({type(error).__name__})")
```

`on_message` receives a typed `Message`; `on_interaction` receives an `Interaction`. Other events receive dictionaries. For an event named `CHANNEL_UPDATE`, the callback name is `on_channel_update`.

Command/component/form decorators already handle their matching interaction. `on_interaction` also runs for the delivered interaction, so avoid acknowledging the same invocation again there. `on_error(event_name, exception)` receives handler errors; without it, the default logger reports a failure without including exception details.

Do not block the event loop with synchronous network calls or long CPU work. Event handlers run as asynchronous tasks; handle side-effect ordering and duplicate delivery in your application when needed.

## Select intents

```python
from agartha import Bot, Intents

bot = Bot(
    token,
    base_url=api_base,
    intents=Intents.SERVERS | Intents.MESSAGES | Intents.MESSAGE_REACTIONS,
)
```

Only request intents approved for the application. Gateway metadata advertises the supported mask; discovery is available with `await bot.client.get_gateway()`.

| Intent | Value | Access |
| --- | --- | --- |
| `Intents.NONE` | `0` | No general event categories |
| `Intents.SERVERS` | `1` | Server, channel, and role lifecycle |
| `Intents.MEMBERS` | `2` | Member events; privileged approval |
| `Intents.MODERATION` | `4` | Ban/moderation events |
| `Intents.PRESENCES` | `256` | Bot presence/activity; privileged approval |
| `Intents.MESSAGES` | `512` | Visible message lifecycle |
| `Intents.MESSAGE_REACTIONS` | `1024` | Visible Unicode reaction lifecycle |
| `Intents.MESSAGE_CONTENT` | `32768` | Authorized human message bodies/embeds; privileged approval |

`Intents.default()` returns `SERVERS | MESSAGES`. The enum also contains `DIRECT_MESSAGES`, but native v1 does not support bot DMs; do not request it. The current native supported mask is `34567`.

Interaction events are addressed to the application even when it subscribes only to server events. Reading human message content separately requires approved `MESSAGE_CONTENT`; otherwise that content is redacted. Bots can read their own content. Server/channel access still applies to events and retained replay.

## Presence

```python
await bot.gateway.update_presence(
    "idle", activities=[{"type": 0, "name": "Preparing a report"}]
)
```

Statuses are `online`, `idle`, `dnd`, or `invisible`. Native presence supports at most one activity name/type record. Presence updates are limited to five per 20 seconds. Do not use an activity string to advertise resource IDs or confidential request details.

## Use GatewayClient directly

```python
from agartha import Client, GatewayClient, Intents


async def dispatch(event_name: str, payload: dict) -> None:
    print(event_name)


async def connect(token: str, api_base: str) -> None:
    async with Client(token, base_url=api_base) as client:
        gateway = GatewayClient(client, intents=Intents.SERVERS, shard=(0, 1))
        try:
            await gateway.run(dispatch)
        finally:
            await gateway.close()
```

```text
GatewayClient(client, *, intents=Intents.SERVERS, shard=(0, 1),
              reconnect_delay=1.0, hello_timeout=15.0)
await gateway.run(dispatch=None)
await gateway.update_presence(status, *, activities=None)
await gateway.send(op, data)
await gateway.close()
```

The shard pair is `(shard_index, shard_count)` with a zero-based index. Use the discovery response's recommended shard count and start budget. `send` is a low-level operation; use the named helpers for ordinary bot work.

## Reconnect and resume

The SDK retains the latest sequence and session ID during the current process. On an eligible reconnect it sends Resume; when the session is no longer resumable it starts a new session. Native retained events and sessions have a 15-minute window. A process restart begins a fresh SDK connection; session state is not automatically persisted to disk.

The SDK monitors heartbeat acknowledgements and reconnects transient transport failures. Discovery's safe GET can retry transient server failures with backoff capped at 30 seconds. Invalid credentials, versions, shards, and unsupported/unapproved intents are terminal errors that need a configuration change.

| Close code | Developer action |
| --- | --- |
| `4004` | Replace revoked/invalid bot credentials; do not reconnect with the same token |
| `4007`, `4009` | Session/sequence is no longer resumable; SDK clears it |
| `4010`, `4011` | Correct the shard settings |
| `4012` | Use a supported Gateway version |
| `4013`, `4014` | Correct unsupported or unapproved intents |
| `4008` | Reduce outgoing activity and review shared quotas |

## Connection limits and envelopes

Discovery returns `url`, `shards`, `supported_intents`, and `session_start_limit` (`total`, `remaining`, `reset_after`, `max_concurrency`). `reset_after` is milliseconds. The SDK observes Identify's five-second concurrency buckets and waits for exhausted start budgets to reset.

Outgoing Gateway frames are limited to 120 per connection per 60 seconds and 4,096 UTF-8 bytes. SDK limiters are local to the running process; server application limits remain authoritative.

For protocol diagnostics, native frames use `{ "op": ..., "d": ..., "s": ..., "t": ... }`:

| Opcode | Meaning |
| --- | --- |
| `0` | Dispatch event |
| `1` | Heartbeat carrying the latest sequence |
| `2` | Identify |
| `3` | Presence update |
| `6` | Resume |
| `7` | Reconnect |
| `9` | Invalid session |
| `10` | Hello with heartbeat interval |
| `11` | Heartbeat acknowledgement |

The SDK handles these connection messages; a command handler should use its `Interaction` methods rather than constructing Gateway frames.
