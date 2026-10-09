# Agartha developer documentation

Build bots for BFO Agartha servers with **Agartha.py**. Use the SDK to register commands, respond in chat, receive events, and call the native API.

## Start building

1. Open [Agartha Developers](https://blufantasy.online/agartha/developers), apply to **BFO Agartha Devs**, and wait for staff approval.
2. Enable and verify two-factor authentication on your BFO account.
3. Create a developer team and application. Generate a bot token in the application settings.
4. Install the application into a test server with the permissions it needs.
5. Follow [Build your first bot](quick-start.md) to install Agartha.py and run `/ping`.

## Choose a guide

| Build | Guide |
| --- | --- |
| A working first bot | [Quick start](quick-start.md) |
| An AI assistant using your own provider | [Build an AI bot](ai-bots.md) |
| Slash commands and right-click actions | [Application commands](commands.md) |
| Buttons, menus, forms, uploads, and private replies | [Replies, menus, and forms](interactions.md) |
| Composed sections, galleries, facts, progress, details, and actions | [Message layouts](message-layouts.md) |
| Classic cards, fields, images, and attribution | [Classic embeds](embeds.md) |
| Messages, channels, members, roles, and moderation | [REST resources and methods](resources.md) |
| Event handlers and bot presence | [Gateway and events](gateway.md) |
| Connect a user's account with consent | [Account authorization](oauth.md) |
| Reliable requests and error handling | [Errors and rate limits](errors-and-limits.md) |
| App subscriptions and team earnings | [Products and earnings](monetization.md) |

## Teams and applications

Applications belong to a developer team. A bot represents its application in the servers where administrators install it.

| Team role | Access |
| --- | --- |
| Owner | Team administration, ownership transfer, credentials, and eligible finance actions |
| Admin | Applications and lower team roles; cannot replace the owner or modify a peer admin |
| Developer | Application development and permitted credential actions |
| Read only | Permitted team and application information |

Invitations expire after seven days. Invitees need approved developer access and verified two-factor authentication. A developer can own up to ten teams; each team can hold up to 75 applications. Monetized ownership transfers require staff review.

New applications begin in development. They are restricted to approved team members and up to 100 server installations until release approval. Request member, presence, or message-content access in the application's **Gateway intents** settings; privileged access requires staff approval.

## Authentication and IDs

Keep bot tokens in your server's secret store or environment. Agartha.py supplies bot authentication for every request. Rotating a token invalidates the previous credential and its Gateway sessions. Never use a BFO login token as a bot token.

Resource IDs are **18-digit decimal strings with a nonzero first digit**. Keep them as strings. Approved developers can right-click a bot, user, or server and choose **Copy ID**. Display usernames and names in chat; use IDs when your program needs a stable resource reference.

```python
from agartha import public_id

server_id = public_id("100000000000000088")
```

An ID identifies a resource; it does not grant permission to access it. Bot installation and account authorization are separate consent flows.

## Current SDK coverage

The native API supports server installations, messages, channels, roles, member moderation, Unicode reactions, Gateway events, slash and context commands, autocomplete, interactive replies, bot-requested forms, and submitted attachments. Account OAuth provides explicit read scopes. App monetization requires the approval and provider setup described in the earnings guide.

General developer voice connections, bot direct messages, user-installed bots, general multipart bot uploads, and custom reaction emoji are not available in native v1. The optional [signed event receiver](signed-events.md) is a utility; outbound HTTP interaction delivery is not an active alternative to the Gateway.

Agartha has its own API. Use the methods and response shapes in this guide rather than substituting another platform's endpoints.
