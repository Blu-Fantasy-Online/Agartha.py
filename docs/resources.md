# REST resources and methods

Use `Client` for API calls, or use `bot.client` inside a running bot. The SDK sends Bot authentication, validates resource references, schedules requests, and decodes responses.

## Client lifecycle

```python
import asyncio
import os

from agartha import Client


async def main() -> None:
    async with Client(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
        timeout=30.0,
        max_retries=3,
    ) as client:
        application = await client.get_application()
        servers = await client.list_servers()
        print(application.name, [server.name for server in servers])


if __name__ == "__main__":
    asyncio.run(main())
```

`base_url` includes `/api/v1`. Keep IDs as 18-digit strings. Use an async context manager or call `await client.close()` during shutdown. `max_retries` applies only to confirmed rate-limit responses; see [errors and limits](errors-and-limits.md).

The remaining snippets assume an open `client` and copied `server_id`, `channel_id`, `message_id`, `role_id`, and `user_id` values.

## Resource models

Typed helpers return immutable model objects. Every model has `.id` and `.raw`; `.raw` retains the response dictionary for fields without a convenience property.

| Model | Properties beyond `id` and `raw` |
| --- | --- |
| `Application` | `name`, `description`, `headline`, `icon_url`, `banner_url`, `website_url`, `docs_url`, `support_url`, `privacy_url`, `terms_url`, `tags`, `supported_languages`, `bot`, `support_server` |
| `BotIdentity` | `application_id`, `name`, `avatar_url` |
| `SupportServer` | `name`, `join_url` |
| `Server` | `name`, `public_id` |
| `Channel` | `name`, `server_id` |
| `Message` | `content`, `channel_id` |
| `Role` | `name` |
| `Member` | Read `username`, `display_name`, `status`, and `joined_at` from `raw` |
| `Resource` | Generic resource object |

`Server.id` and `Server.public_id` refer to the same server identity. An optional related ID may be `None`. Do not substitute an ID for a missing display name.

Read [bot identity and profiles](bot-identity.md) for application metadata, image uploads, and native support links. Missing optional profile text and URLs return `None`; tags and supported languages return immutable tuples.

## Applications, servers, and channels

| Agartha.py call | Return | API method and path |
| --- | --- | --- |
| `get_application()` | `Application` | `GET /applications/@me` |
| `list_servers()` | `list[Server]` | `GET /servers` |
| `get_server(server_id)` | `Server` | `GET /servers/{server_id}` |
| `list_channels(server_id)` | `list[Channel]` | `GET /servers/{server_id}/channels` |
| `get_channel(channel_id)` | `Channel` | `GET /channels/{channel_id}` |
| `get_gateway()` | `dict` | `GET /gateway/bot` |

```python
server = await client.get_server(server_id)
channels = await client.list_channels(server.id)
text_channels = [channel for channel in channels if channel.raw.get("kind") == "text"]
```

The bot sees enabled installations and visible channels. Channel/category overrides apply to each request. A resource becoming inaccessible can produce `Forbidden` or `NotFound` even if your bot read it earlier.

## Messages and pagination

```python
from agartha import action_row, button

message = await client.create_message(
    channel_id,
    content="Choose an action.",
    nonce="welcome-post-2026-10-08",
    components=[action_row(button("welcome:help", "Help"))],
)
message = await client.edit_message(
    channel_id, message.id, content="Welcome to the server.", components=[]
)
```

Messages accept up to 2,000 content characters, ten embeds, and five component rows. An embed-only message is supported. Classic cards have a combined 6,000-character text limit and a 32,000-byte representation limit. Messages containing [layouts](message-layouts.md) allow up to three layouts, 40 blocks, 12,000 combined text characters, and 48,000 embed bytes; classic text still fits within 6,000 characters. Complete message data must fit within 60,000 bytes. Use HTTPS links for media and links. Mention alerts are suppressed by default; see [explicit mention alerts](interactions.md#explicit-mention-alerts) for bounded recipients and server policy.

| Agartha.py call | Return |
| --- | --- |
| `list_messages(channel_id, **params)` | `list[Message]` |
| `create_message(channel_id, *, content=None, nonce=None, allowed_mentions=None, **fields)` | `Message` |
| `get_message(channel_id, message_id)` | `Message` |
| `edit_message(channel_id, message_id, **fields)` | `Message` |
| `delete_message(channel_id, message_id)` | `None` |
| `mention_user(user_id)` | Public user/bot reference string; no alert authority |
| `mention_role(role_id)` | Public role reference string; no alert authority |
| `allowed_mentions(*, users=(), roles=())` | Explicit recipient dictionary, at most 20 users/bots and five roles |

Message lists are newest first. `limit` defaults to 50 and is capped at 100. `before` accepts a message ID from that channel:

```python
page = await client.list_messages(channel_id, limit=25)
older = (
    await client.list_messages(channel_id, limit=25, before=page[-1].id)
    if page else []
)
```

Only `before` pagination is currently implemented for message history. Lists include only currently visible messages. This is a bounded history API, not a guaranteed complete export. Human message content requires approved `MESSAGE_CONTENT` access; the application's own message content is readable without that privileged intent. Encrypted server content is unavailable to bots.

A bot can edit only its own messages. Deleting another author's message requires `manage_messages`; ordinary posting requires `send_messages`. A stable `nonce` identifies a specific create operation: retrying the same creation with the same payload and nonce returns its prior message when still accessible. Changing the payload under that nonce is a conflict. Do not reuse a nonce for a different message.

## Reactions

```python
await client.add_reaction(channel_id, message_id, "✅")
reactions = await client.list_reactions(channel_id, message_id, "✅")
await client.remove_reaction(channel_id, message_id, "✅")
```

`list_reactions(...)` returns a list of dictionaries with `user_id`/`bot_id` references or `None`. Mutation helpers act on the bot's own reaction. Unicode emoji are URL-encoded by the SDK. Custom emoji and removing another principal's reaction are unavailable through these helpers.

## Members, roles, and audit logs

```python
member = await client.get_member(server_id, user_id)
name = member.raw.get("display_name") or member.raw.get("username")
roles = await client.list_roles(server_id)
```

| Agartha.py call | Return | Requirement |
| --- | --- | --- |
| `get_member(server_id, user_id)` | `Member` | Visible current member in the installed server |
| `list_members(server_id, **params)` | `list[Member]` | Approved Members intent |
| `list_roles(server_id)` | `list[Role]` | Server visibility |
| `list_audit_logs(server_id, **params)` | `list[dict]` | `view_audit_log` |

Member and audit lists currently provide up to 100 records in an initial bounded page. Although the SDK accepts query keywords, additional cursor pagination is not implemented for these lists. Use the single-member method for a known user. Audit responses include only authorized server activity.

A member response exposes names and status, for example:

```json
{
  "id": "100000000000000039",
  "public_id": "100000000000000039",
  "username": "DrHeretic",
  "display_name": "DrHeretic",
  "status": "active",
  "joined_at": "2026-10-08T12:00:00Z"
}
```

## Generic API calls

For supported operations without a named helper, use:

```text
await client.request(method, path, *, json=None, params=None, binary=False)
```

Paths are relative to `/api/v1`. Provide query values in `params`, not in the path. Request bodies are JSON with a 65,536-byte limit. Generic calls return a dictionary, list, or `None` for HTTP 204. Resource references in the path cannot be overridden in the body.

```python
channel = await client.request(
    "POST", f"/servers/{server_id}/channels",
    json={"name": "bot-updates", "kind": "text", "topic": "Application updates"},
)
```

| Action through `client.request` | Supported body | Permission |
| --- | --- | --- |
| `POST /servers/{server_id}/channels` | `name`, `kind`, optional `topic` | `manage_channels` |
| `PATCH /channels/{channel_id}` | `name` and/or `topic` | `manage_channels` |
| `DELETE /channels/{channel_id}` | None | `manage_channels` |
| `PUT /channels/{channel_id}/pins/{message_id}` | None | `manage_messages` |
| `DELETE /channels/{channel_id}/pins/{message_id}` | None | `manage_messages` |
| `POST /channels/{channel_id}/threads` | `content`, optional `title`, message fields | `manage_threads` and `send_messages` |
| `POST /servers/{server_id}/roles` | `name`, `permissions`, optional `position` | `manage_roles` |
| `PATCH /servers/{server_id}/roles/{role_id}` | `name`, `permissions`, and/or `position` | `manage_roles` |
| `DELETE /servers/{server_id}/roles/{role_id}` | None | `manage_roles` |
| `PUT /servers/{server_id}/members/{user_id}/roles/{role_id}` | None | `manage_roles` |
| `DELETE /servers/{server_id}/members/{user_id}/roles/{role_id}` | None | `manage_roles` |
| `DELETE /servers/{server_id}/members/{user_id}` | None | `kick_members` |
| `PUT /servers/{server_id}/bans/{user_id}` | None | `ban_members` |
| `GET /applications/@me/entitlements` | None | This application's authorized entitlements |

Channel creation supports `text`, `forum`, `document`, `calendar`, `media`, and `announcement`. Message creation supports text/media/forum destinations. Use `parent_id` to reply inside an accessible unlocked thread.

```python
result = await client.request(
    "PUT", f"/servers/{server_id}/members/{user_id}/roles/{role_id}"
)
```

Role and member changes respect hierarchy. Bots cannot change the server owner, higher/equal members, default roles, or another application's managed role. New/edited role permissions cannot exceed the bot's current authority or its installation grant. Native v1 moderation routes target current members; an unban or unrestricted offline-ban endpoint is not provided.

## Permission handling

Server administrators approve an installation's permission ceiling. The current managed role and channel/category overrides can reduce that authority. Having the right intent does not bypass permissions; having a permission does not grant a privileged intent.

Common permission names are `view_channel`, `send_messages`, `manage_messages`, `manage_threads`, `manage_channels`, `manage_roles`, `kick_members`, `ban_members`, and `view_audit_log`. Request only what your bot needs and handle a permission loss normally.

Use [interaction helpers](interactions.md) for callback and follow-up routes and [OAuthClient](oauth.md) for user-authorized reads.
