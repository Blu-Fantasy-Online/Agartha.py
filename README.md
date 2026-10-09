# Agartha.py

Async Python SDK for building applications and bots on **BFO Agartha**. Version **0.5.0** adds typed bot profiles, application metadata, and native support server links alongside REST calls, Gateway events, application commands, message layouts, interactive replies, menus, forms, submitted attachments, and account OAuth.

**Python 3.12+** is required. Runtime dependency: `aiohttp==3.14.4`. The optional `webhooks` extra adds `PyNaCl==1.6.2` for the signed receiver utility.

## Install

Download the [published wheel](https://github.com/Blu-Fantasy-Online/Agartha.py/releases/download/v0.5.0/agartha_py-0.5.0-py3-none-any.whl) and install it:

```text
python -m pip install ./agartha_py-0.5.0-py3-none-any.whl
```

Official SDK releases, examples, checksums, and issue tracking are available in the [BFO Agartha.py repository](https://github.com/Blu-Fantasy-Online/Agartha.py). Install the published wheel until a public package registry release is announced.

Agartha.py is proprietary software owned by Blu Fantasy Online LLC. The [SDK license](https://github.com/Blu-Fantasy-Online/Agartha.py/blob/main/LICENSE) permits developing and running your own bots, including commercial bots, using official unmodified releases. It prohibits unauthorized redistribution, modification, reverse engineering, and recreating the SDK or platform. Documentation examples may be adapted in your own bots. Third-party dependency licenses remain separate.

## First bot

Apply through [Agartha Developers](https://blufantasy.online/agartha/developers), create a team/application after approval, generate a bot token, and install the app into a test server.

```python
import asyncio
import os

from agartha import Bot, Interaction, Intents

bot = Bot(
    os.environ["AGARTHA_BOT_TOKEN"],
    base_url=os.environ["AGARTHA_API_BASE_URL"],
    intents=Intents.SERVERS,
)


@bot.command(name="ping", description="Check the connection")
async def ping(interaction: Interaction) -> None:
    await interaction.respond("Pong!", ephemeral=True)


async def main() -> None:
    try:
        # Run explicitly when registering the complete command set for this scope:
        # await bot.sync_commands(server_id=os.environ["AGARTHA_TEST_SERVER_ID"])
        await bot.start()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
```

`AGARTHA_API_BASE_URL` normally uses `https://agartha-api.blufantasy.online/api/v1`; use the endpoint provided by the developer panel. Store the token in server-side secrets. Resource IDs are 18-digit strings; keep them as strings and display usernames/names in chat.

## Guides and method reference

The [developer documentation](https://blufantasy.online/agartha/developers/docs) contains the complete SDK-first guide. Its source is maintained in `docs/agartha-developers` in the BFO repository.

| Guide | Covers |
| --- | --- |
| [Quick start](https://blufantasy.online/agartha/developers/docs?doc=quick-start) | Install, run, register, and test a bot |
| [Bot identity](https://blufantasy.online/agartha/developers/docs?doc=bot-identity) | Profile images, tags, languages, useful links, and native support servers |
| [Build an AI bot](https://blufantasy.online/agartha/developers/docs?doc=ai-bots) | Your own provider, scoped text history, private commands, and bounded requests |
| [Application commands](https://blufantasy.online/agartha/developers/docs?doc=commands) | Slash options, groups, autocomplete, and user/message actions |
| [Interactions](https://blufantasy.online/agartha/developers/docs?doc=interactions) | Replies, defer, follow-ups, components, forms, and attachments |
| [Message layouts](https://blufantasy.online/agartha/developers/docs?doc=message-layouts) | Native blocks, galleries, progress, and placed actions |
| [Classic embeds](https://blufantasy.online/agartha/developers/docs?doc=embeds) | Rich cards, attribution, and message budgets |
| [REST resources](https://blufantasy.online/agartha/developers/docs?doc=resources) | Typed helpers and generic API operations |
| [Gateway](https://blufantasy.online/agartha/developers/docs?doc=gateway) | Events, intents, presence, and resume |
| [OAuth](https://blufantasy.online/agartha/developers/docs?doc=oauth) | Consent, PKCE, account reads, refresh, and revocation |
| [Errors and limits](https://blufantasy.online/agartha/developers/docs?doc=errors-and-limits) | Retry behavior, permissions, deadlines, and quotas |
| [Products and earnings](https://blufantasy.online/agartha/developers/docs?doc=monetization) | Entitlements, team fees, and cashout |
| [Signed receiver](https://blufantasy.online/agartha/developers/docs?doc=signed-events) | Optional signature-verification utility |

Use `Client` for REST-only work. Typed resources retain their response fields in `.raw`. Generic `client.request(...)` handles documented actions without a convenience method.

The SDK learns response rate buckets and retries only confirmed HTTP 429 responses. Other failures are not automatically replayed. Defer interactions before long work; initial acknowledgements have a three-second deadline, and follow-ups have a 15-minute window.

Native v1 does not provide general developer voice connections, bot DMs, user-installed bots, general multipart bot uploads, custom reaction emoji, or an active outbound HTTP interaction service. Refer to the guide for current supported methods and application approval requirements.

## Native message layouts

Compose a message from headings, text, sections, galleries, dividers, facts, callouts, progress, expandable details, and actions. Layouts use Agartha's native presentation schema and work in channel messages, private replies, updates, and follow-ups.

```python
from agartha import MessageLayout, action_row, button, message_payload

layout = (MessageLayout(accent=0x21C3B2)
          .add_heading("Community update", level=1)
          .add_section("A new season starts Friday.", title="Explore what is coming")
          .add_facts({"label": "Starts", "value": "Friday · 6:00 PM"},
                     {"label": "Where", "value": "Community lounge"}, columns=2)
          .add_progress("Launch preparations", 8, 10, unit="tasks")
          .add_callout("Everyone is welcome.", tone="success")
          .add_details("What to bring", "Bring your ideas and a friend.")
          .add_actions({"custom_id": "join"},
                       {"label": "Read guide", "url": "https://example.org/guide/"}))
payload = message_payload(layout, components=[action_row(button("join", "Join"))])
# In a handler: await interaction.respond(**payload)
```

`MessageLayout.to_dict()` returns `{"layout": {"version": 1, "blocks": [...]}}`. Import the inner object with `MessageLayout.from_dict(payload["layout"])`. Builders validate each edit atomically and return themselves for chaining. All media and external actions use absolute HTTPS URLs; image descriptions and spoiler flags are supported.

An action is either `{"custom_id": "join"}`, referencing an existing message button or select, or `{"label": "Read guide", "url": "https://example.org/guide/"}`. Each callback reference occupies one layout position per message. `message_payload(*cards, components=[...], **data)` validates complete payloads and resolves references against their canonical message components. Existing `button`, `string_select`, `entity_select`, and `action_row` builders remain available. A referenced component retains its current permissions, disabled state, and interaction handler.

`embed_payloads(*cards)` accepts both `MessageLayout` and `Embed` instances, as well as their validated dictionaries. A message supports ten cards total, up to three native layouts, twenty blocks per layout, and forty layout blocks total. Classic card text keeps its combined 6,000-character limit. When layouts are present, all visible card text together fits 12,000 characters and encoded card data fits 48,000 UTF-8 bytes; classic-only card data fits 32,000 bytes. Media descriptions, facts, progress units, and external action labels count toward visible text. URLs and callback references do not. Complete message payloads fit 60,000 bytes.

The SDK also validates message and interaction writes before transport. Partial edits without a `components` field may retain existing references; the server validates those references against the saved components. Supplying `components=[]` explicitly clears them and cannot leave a layout pointing at a removed action. Server validation remains authoritative for current permissions and retained state.

`examples/message_layouts.py` demonstrates an interactive layout using the existing command and component handlers.

## Classic rich cards

```python
from agartha import Embed, embed_payloads

card = (Embed("Application status", "Ready", color=0x21C3B2)
        .add_field("Connection", "Online", inline=True)
        .set_footer("Your application"))
payload = embed_payloads(card)
# In a handler: await interaction.respond(ephemeral=True, embeds=payload)
```

`Embed.to_dict()` returns one validated dictionary; `embed_payloads(*cards)` checks the complete message budgets described above. Fields, author/footer icons and links, HTTPS images/thumbnails, and timezone-aware timestamps are supported. Invalid edits raise `ValueError` while preserving the previous builder state. `examples/rich_embeds.py` provides a runnable slash command.

## Bot identity and profiles

`await client.get_application()` returns an `Application` with typed description, headline, image URLs, website and documentation links, tags, and supported languages. `application.bot` is a `BotIdentity` with its own public ID, application ID, name, and avatar URL. An active native support invite appears as `application.support_server`, a `SupportServer` with its name and join URL.

Configure the profile and upload icons or banners through the authenticated developer portal. Optional text and links return `None` when unset; tags and languages return immutable tuples. Existing response fields remain available in `.raw`. `examples/bot_identity.py` reads the profile and builds a message layout preview without posting it.

## AI assistants

`AIAssistant` accepts your async provider callable, which receives `AIRequest(messages, max_output_chars)` and returns plain text. `AISessionKey.from_interaction(interaction)` scopes local history by application, server, channel, and invoking user. Configure context, turn, request, session, output, and timeout limits; use `clear(scope)` for forgetting and `close()` for shutdown. AI errors inherit `AIError` and suppress raw provider details.

`examples/ai_assistant.py` is a complete `/ask` and `/forget` bot with an optional Chat Completions-compatible adapter. Run it on your own server with your own provider endpoint, model, and key. The adapter does not forward Agartha credentials or IDs, exposes no server tools, refuses redirects/tool responses, and caps response bytes. Local AI helpers do not grant Agartha permissions; each API write remains server-authorized. Provider calls are not retried automatically.

## Developing the SDK

From this package directory:

```text
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests examples
python -m mypy src
python -m build
```

Tests use local HTTP and WebSocket fixtures. They validate request handling, dynamic rate limits, errors, Gateway heartbeat/resume, command dispatch, forms, attachments, OAuth, signature verification, rich card contracts, AI scope isolation, capacity, timeout/cancellation, and provider adapters without contacting live services.

`examples/echo.py` demonstrates explicit command synchronization. `examples/diagnostics.py` reads the supported API; its optional write checks belong only in an authorized test installation. `examples/oauth_user.py` illustrates account authorization. `examples/signed_events.py` runs the optional receiver utility on loopback.
