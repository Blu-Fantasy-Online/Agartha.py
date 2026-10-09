# Message layouts

Use **MessageLayout** in Agartha.py 0.4.0 to compose a message from ordered blocks. Put a heading beside an action, group media into a gallery, display structured facts, show progress, or offer expandable details. The same layout works in public messages, private command replies, original-response edits, and follow-ups.

Open **Message Studio** in your developer workspace to start from a welcome, release, event, or AI answer template. Add, reorder, and edit blocks while viewing the chat preview. Export validated JSON or Agartha.py code. The preview does not send messages; your running bot publishes the exported payload.

## Build a layout

```python
from agartha import MessageLayout, embed_payloads

layout = (
    MessageLayout(accent=0x26D5CD)
    .add_heading("Welcome to your community")
    .add_text("Find your next conversation and make yourself at home.")
    .add_section(
        "Discover communities, conversations, and events.",
        title="Explore Agartha",
        accessory={
            "label": "Explore",
            "url": "https://www.blufantasy.online/agartha/discover",
        },
    )
    .add_divider()
    .add_facts(
        {"label": "Starts", "value": "Friday · 6:00 PM"},
        {"label": "Location", "value": "Community lounge"},
    )
    .add_progress("Event places", 68, 100, unit="members")
    .add_details("What to bring", "Bring your questions and ideas.")
)

await interaction.respond(
    embeds=embed_payloads(layout),
    allowed_mentions={"parse": []},
)
```

Layout text supports a safe subset of Markdown: headings, emphasis, lists, links, and code. Raw HTML, scripts, custom CSS, and iframes are unavailable. Text and labels do not grant mention or ping authority. Use readable names in your message.

## Place buttons and menus

A callback action stays in the message's ordinary `components` array. Place it within a layout by referencing its `custom_id`. Link actions instead supply a label and HTTPS URL and do not invoke the bot.

```python
from agartha import MessageLayout, action_row, button, embed_payloads

layout = (
    MessageLayout(accent=0x26D5CD)
    .add_section(
        "Refresh the current application status.",
        title="Application status",
        accessory={"custom_id": "status:refresh"},
    )
    .add_actions({
        "label": "Read the guide",
        "url": "https://www.blufantasy.online/agartha/developers/docs",
    })
)

await interaction.respond(
    ephemeral=True,
    embeds=embed_payloads(layout),
    components=[action_row(button("status:refresh", "Refresh"))],
)


@bot.component("status:refresh")
async def refresh_status(interaction):
    refreshed = MessageLayout().add_callout(
        "The application is ready.", title="Status refreshed", tone="success"
    )
    await interaction.update(embeds=embed_payloads(refreshed), components=[])
```

Every placed callback must exist in that message's components. Place each `custom_id` once. String and resource menus can be placed in an actions block through the same reference mechanism. Unplaced controls appear below the message. Current installation, channel access, command permissions, and source-message checks still apply when a reader clicks an action.

Edits validate the resulting message. If you remove a referenced component, remove its layout placement in the same edit. If you replace the entire layout, send its new components in that edit as needed. Existing message and private-response permissions remain in force.

## Galleries and information blocks

```python
layout = (
    MessageLayout()
    .add_heading("Release highlights")
    .add_gallery(
        {"url": "https://example.org/releases/overview.png", "alt": "Release overview"},
        {"url": "https://example.org/releases/details.png", "alt": "New areas", "spoiler": True},
    )
    .add_callout("Available to your community today.", title="Release ready", tone="info")
    .add_facts({"label": "Version", "value": "2.4"}, columns=1)
)
```

Use image URLs available over HTTPS and describe their content with `alt`. Spoiler media starts concealed until the reader chooses to reveal it. Media references do not upload, generate, or execute anything. A progress block displays the values your bot supplies; your bot remains responsible for computing and updating them.

For an AI bot, defer before calling your provider, then compose its bounded output with `add_text`, source links with `add_actions`, and an optional explanation with `add_details`. Treat provider output as untrusted data and validate it before sending. Agartha does not provide AI hosting or provider credits through message layouts. See [Build an AI bot](ai-bots.md) for provider handling.

## Builder reference

Every `add_*` method validates the update, returns the same builder, and preserves its previous state if validation fails.

| Call | Block |
| --- | --- |
| `MessageLayout(*, accent=None)` | Create a version-1 layout |
| `add_heading(text, *, level=...)` | Heading, with level 1, 2, or 3 |
| `add_text(text)` | Markdown body text |
| `add_section(text, *, title=None, thumbnail=None, accessory=None)` | Text with an optional image or action |
| `add_gallery(*items)` | One to six image items |
| `add_divider(*, spacing=...)` | Small or large separation |
| `add_facts(*items, columns=...)` | Structured label/value pairs |
| `add_callout(text, *, title=None, tone=...)` | Info, success, warning, or danger notice |
| `add_progress(label, value, total, *, unit=None)` | Labelled, bounded progress |
| `add_details(title, text)` | Reader-controlled expandable text |
| `add_actions(*items)` | One to five callback references or link actions |
| `MessageLayout.from_dict(data)` | Validate and copy the inner layout object |
| `to_dict()` | Return an independent `{"layout": {...}}` embed dictionary |
| `embed_payloads(*cards)` | Validate layouts and classic cards together |

## JSON contract

Layouts use the existing `embeds` field. A layout embed contains only `layout`; classic embed fields belong in a separate card. There is no additional message flag or new endpoint.

```json
{
  "embeds": [{
    "layout": {
      "version": 1,
      "accent": 2545101,
      "blocks": [
        {"type": "heading", "text": "Community update"},
        {"type": "section", "title": "Next event", "text": "Friday at 6:00 PM", "accessory": {"custom_id": "event:join"}},
        {"type": "progress", "label": "Event places", "value": 68, "total": 100, "unit": "members"}
      ]
    }
  }],
  "components": [{"type": 1, "components": [{"type": 2, "style": 1, "custom_id": "event:join", "label": "Join event"}]}],
  "allowed_mentions": {"parse": []}
}
```

| Block | Accepted properties after `type` |
| --- | --- |
| `heading` | Required `text`; optional integer `level` from 1 to 3 |
| `text` | Required `text` |
| `section` | Required `text`; optional `title`, `thumbnail: {url, alt?}`, and `accessory` action |
| `gallery` | Required `items` array of `{url, alt?, spoiler?}` |
| `divider` | Optional `spacing`: `small` or `large` |
| `facts` | Required `items` array of `{label, value}`; optional integer `columns` from 1 to 3 |
| `callout` | Required `text`; optional `title` and `tone`: `info`, `success`, `warning`, or `danger` |
| `progress` | Required `label`, `value`, and `total`; optional `unit` |
| `details` | Required `title` and `text` |
| `actions` | Required `items` array of actions |

An action is exactly `{"custom_id": "callback-name"}` or `{"label": "Open guide", "url": "https://example.org/guide/"}`. Blocks are ordered and flat; nested layouts and unsupported properties are rejected.

## Limits

| Resource | Limit |
| --- | --- |
| All embeds per message | 10, including layouts and classic cards |
| Layouts per message | 3 |
| Blocks | 20 per layout; 40 across the message |
| Heading or title | 256 characters |
| Text body | 4,096 characters per block |
| Gallery items / image alt text | 6 per gallery / 256 characters |
| Fact items / label / value | 12 per block / 64 / 512 characters |
| Action items / link label / callback reference | 5 per block / 80 / 100 characters |
| Progress label / unit | 256 / 32 characters |
| Progress numbers | Finite, `0 <= value <= total`, and `0 < total <= 1,000,000,000,000` |
| Classic-card text | 6,000 characters across classic cards |
| Combined text with layouts | 12,000 characters across layouts and classic cards |
| Encoded embeds with layouts | 48,000 UTF-8 bytes; classic-only messages retain 32,000 bytes |
| Complete message data | 60,000 bytes; component limits still apply |
| Accent | Integer `0` through `16777215` |
| Every media/link URL | Absolute HTTPS, at most 2,048 characters; no credentials, whitespace, backslashes, or custom ports |

Visible titles, text, facts, image descriptions, action labels, and units count toward the shared character budget. URLs and callback references count toward the separate encoded byte budget. Counts use Unicode characters, not JavaScript string length. The server independently checks the payload and its action references before saving it.

See [classic embeds](embeds.md) for existing card builders and [replies, menus, and forms](interactions.md) for response and interaction handling.
