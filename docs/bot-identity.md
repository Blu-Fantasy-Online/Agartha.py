# Bot identity and profiles

Give your application an identity people can recognize in chat and understand before installing it. Configure its profile in the [Agartha developer portal](https://www.blufantasy.online/agartha/developers), then read that identity with Agartha.py.

The typed profile models in this guide require **Agartha.py 0.5.0 or newer**. See [Quick start](quick-start.md) for installation.

An application and its bot have separate public IDs. The application's ID identifies its configuration and commands; the bot's ID identifies the account representing it in servers. Both are 18-digit strings. Use their names when presenting a profile or replying in chat.

## Configure your application profile

Choose your team and application in the developer portal, then open **Applications → Identity → Application identity**. Edit its profile with the access granted by your team role. The preview shows how the current draft will appear.

| Profile field | Purpose and limit |
| --- | --- |
| Name | The application and bot name, up to 80 characters |
| Description | Explain what the application does, up to 4,000 characters |
| Headline | A short introduction, up to 120 characters |
| Icon | Upload the image used for the application icon and bot avatar |
| Banner | Upload a wider image for the bot profile |
| Tags | Up to ten unique tags, each 1–24 characters: lowercase letters, digits, and hyphens; start with a letter or digit |
| Supported languages | Up to twenty unique language tags, each up to 35 characters, such as `en`, `en-US`, and `zh-Hant` |
| Website | Your application's main HTTPS website |
| Documentation | HTTPS instructions for using your application |
| External support | An HTTPS support website, separate from the native support server |
| Privacy policy and terms | HTTPS pages explaining your application's data handling and terms |
| Agartha support server | An active native server invite that opens the community where people can get help |

Tags are trimmed and converted to lowercase when saved. Language tags preserve their case and must be unique regardless of case. Language validation accepts 2–8 letters followed by optional hyphen-separated segments of 1–8 letters or digits.

In **Appearance**, choose a PNG, JPEG, or WebP file and inspect its local preview, then select **Upload icon** or **Upload banner**. An icon can be up to 5 MiB; a banner can be up to 8 MiB. Uploading prepares the image in your draft; **Save application** attaches it to the application and publishes the profile changes. You can also use **Use image URLs** to supply an HTTPS image link.

In **Profile**, update the name, headline, description, tags, and languages. **Community & links** contains your website, documentation, and Agartha support invite. Existing privacy policy, terms, and external support links remain available. Each link field allows up to 2,048 characters. Leave an optional field empty to remove it.

## Link a native support server

Create an active invite in the Agartha server where you provide support, then set it on your application. Publishing that link requires current access to the server and permission to invite members. The developer portal validates the invite before saving it.

The API returns the support server's public ID, name, and join URL while its invite remains active. If the invite expires, is revoked, reaches its usage limit, or its server becomes unavailable, `application.support_server` becomes `None` on the next read. Handle that as an ordinary optional link.

The external `support_url` remains available for a help website. It does not determine the native support server.

## Read identity with Agartha.py

```python
import asyncio
import os

from agartha import Client


async def main() -> None:
    async with Client(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
    ) as client:
        application = await client.get_application()
        print(application.name, application.headline or "")
        print("Tags:", ", ".join(application.tags))
        print("Languages:", ", ".join(application.supported_languages))

        if application.bot is not None:
            print("Bot:", application.bot.name)
        if application.support_server is not None:
            print("Support:", application.support_server.name)
            print(application.support_server.join_url)


if __name__ == "__main__":
    asyncio.run(main())
```

`client.get_application()` calls `GET /applications/@me`. It reads the application belonging to the bot token. Profile uploads and changes use your authenticated developer portal session.

| Model | Typed properties |
| --- | --- |
| `Application` | `id`, `name`, `description`, `headline`, `icon_url`, `banner_url`, `website_url`, `docs_url`, `support_url`, `privacy_url`, `terms_url`, `tags`, `supported_languages`, `bot`, `support_server`, `raw` |
| `BotIdentity` | `id`, `application_id`, `name`, `avatar_url`, `raw` |
| `SupportServer` | `id`, `name`, `join_url`, `raw` |

Optional text and URL properties return `None` when absent, `null`, or empty. Optional collections return empty tuples. `tags` and `supported_languages` are tuples of strings; they retain the order returned by the API. `bot` and `support_server` return a model or `None`. Every model retains its response dictionary in `raw`, including additional fields without a convenience property.

## Show a profile in chat

Use [message layouts](message-layouts.md) to present a bot's description, supported languages, and useful links. The application icon can be a section thumbnail, and its banner can be a gallery image.

```python
from agartha import MessageLayout, message_payload

application = await client.get_application()
layout = MessageLayout(accent=0x21C3B2).add_heading(application.name)
if application.headline:
    layout.add_text(application.headline)
layout.add_section(
    application.description or "Explore this application's commands.",
    thumbnail={"url": application.icon_url, "alt": application.name}
    if application.icon_url else None,
)
if application.banner_url:
    layout.add_gallery({"url": application.banner_url, "alt": application.name})

links = []
if application.docs_url:
    links.append({"label": "Documentation", "url": application.docs_url})
if application.support_server:
    links.append({"label": "Join support", "url": application.support_server.join_url})
if links:
    layout.add_actions(*links)

await interaction.respond(ephemeral=True, **message_payload(layout))
```

The snippet assumes an open `client` and a command `interaction`. Link actions need no component callback. For a complete read-only identity example, see `examples/bot_identity.py` in the SDK examples.

Identity settings do not grant installation permissions, privileged intents, or release approval. Continue to configure those separately in the application panel.
