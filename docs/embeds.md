# Classic embeds

Use `Embed` to build rich chat cards with headings, text, fields, media, author attribution, and a footer. Convert cards to plain request dictionaries with `embed_payloads(...)`; the same payload works with message creation, initial interaction replies, edits, and follow-ups.

For ordered sections, media galleries, progress, expandable details, and actions placed alongside content, use [Message layouts](message-layouts.md) with Agartha.py 0.4.0. Classic cards remain supported and can appear alongside layouts. Their text budget stays at 6,000 characters; a message containing layouts has a 12,000-character combined budget and a 48,000-byte embed budget.

## Build a card

```python
from datetime import UTC, datetime

from agartha import Embed, Interaction, embed_payloads


@bot.command(name="status", description="Show application status")
async def status(interaction: Interaction) -> None:
    card = (
        Embed(
            "Application status",
            "Ready to answer commands.",
            color=0x21C3B2,
            timestamp=datetime.now(UTC),
        )
        .set_author("Community assistant", url="https://blufantasy.online/")
        .add_field("Connection", "Online", inline=True)
        .add_field("Replies", "Private", inline=True)
        .set_footer("Requested by you")
    )
    await interaction.respond(ephemeral=True, embeds=embed_payloads(card))
```

Messages suppress mentions by default. Write readable names in the card; plain text does not grant permission to ping accounts or roles. `ephemeral=True` makes this response visible only to the invoker.

## Images, thumbnails, and attribution

```python
card = (
    Embed("Release notes", "The latest changes are ready.",
          url="https://example.org/releases/", color=0x21C3B2)
    .set_author("Your application", icon_url="https://example.org/app-icon.png")
    .set_image("https://example.org/release-banner.png")
    .set_thumbnail("https://example.org/release-icon.png")
    .set_footer("Published by your team", icon_url="https://example.org/team.png")
)
```

Media URLs must already be available over HTTPS. An embed references an image; it does not upload or generate it. General bot file uploads are not currently provided. Use stable URLs you control and avoid including secrets in them. The chat displays image and thumbnail media, author attribution, and footer attribution when present.

## Send, edit, and follow up

```python
payload = embed_payloads(Embed("Release ready", "Your application is online."))
message = await client.create_message(channel_id, embeds=payload)
await client.edit_message(channel_id, message.id, embeds=payload)
```

For interactions, acknowledge the request before longer work:

```python
await interaction.defer(ephemeral=True)
await interaction.edit_original(embeds=payload)
await interaction.followup(embeds=payload, flags=64)
```

`embeds=[]` clears cards in an edit. An initial message still needs visible content, embeds, or components. Each API call checks the application's current installation and permissions; successful local validation does not authorize a write.

## Builder reference

| Call | Result |
| --- | --- |
| `Embed(title=None, description=None, *, url=None, color=None, timestamp=None)` | Create a validated card; all fields are optional |
| `add_field(name, value, *, inline=False)` | Append a field and return the same builder |
| `set_author(name, *, url=None, icon_url=None)` | Replace author attribution and return the builder |
| `set_footer(text, *, icon_url=None)` | Replace footer attribution and return the builder |
| `set_image(url)` | Set the main image and return the builder |
| `set_thumbnail(url)` | Set the thumbnail and return the builder |
| `Embed.from_dict(data)` | Validate and copy an existing card dictionary |
| `to_dict()` | Return an independent validated dictionary for one card |
| `embed_payloads(*cards)` | Validate the complete group of builders/dictionaries and return a list |

Use `embed_payloads(card1, card2)` when sending multiple cards so the combined text and byte budgets are checked. Changing a returned dictionary does not change the builder. An invalid builder edit raises `ValueError` and preserves its previous fields.

## Limits and accepted fields

| Field | Limit |
| --- | --- |
| Cards per message | 10 |
| Title | 256 characters |
| Description | 4,096 characters |
| Fields per card | 25 |
| Field name / value | 256 / 1,024 characters; both required and nonempty |
| Author name | 256 characters; required when an author is present |
| Footer text | 2,048 characters; required when a footer is present |
| Combined card text per message | 6,000 characters across all titles, descriptions, fields, author names, and footer text |
| Encoded card payload | 32,000 UTF-8 bytes; Unicode and URLs count toward this separate budget |
| Color | Integer `0` through `16777215`, such as `0x21C3B2` |
| Every URL | Absolute HTTPS, at most 2,048 characters, no credentials, whitespace, backslashes, or nonstandard ports |
| Timestamp | Timezone-aware `datetime` or a real RFC3339 timestamp string, at most 40 characters |

URL query strings and fragments require a path separator, such as `https://example.org/?release=1`. The default HTTPS port is allowed. Timestamps use `YYYY-MM-DDTHH:MM:SS`, optionally one to nine fractional digits, followed by `Z` or `±HH:MM`.

Top-level fields are `title`, `description`, `url`, `color`, `timestamp`, `author`, `footer`, `image`, `thumbnail`, and `fields`. Author accepts `name`, `url`, and `icon_url`; footer accepts `text` and `icon_url`; image/thumbnail accept `url`; fields accept `name`, `value`, and boolean `inline`. Unsupported keys are rejected.

The SDK raises `ValueError` before a request for invalid cards. The server independently validates message payloads. See [errors and limits](errors-and-limits.md) for API failures and [replies, menus, and forms](interactions.md) for the response lifecycle. The complete runnable example is `packages/agartha-py/examples/rich_embeds.py` in the source package.
