"""Read the application's native profile and compose a preview without posting it."""

import asyncio
import json
import os

from agartha import Application, Client, MessageLayout, message_payload


def profile_layout(application: Application) -> MessageLayout:
    layout = MessageLayout(accent=0x21C3B2).add_heading(application.name or "Application")
    if application.headline:
        layout.add_text(application.headline)
    layout.add_section(
        application.description or "Explore this application's commands.",
        thumbnail={"url": application.icon_url, "alt": application.name}
        if application.icon_url else None,
    )
    if application.banner_url:
        layout.add_gallery({"url": application.banner_url, "alt": application.name})
    if application.supported_languages:
        layout.add_details("Supported languages", ", ".join(application.supported_languages))
    if application.tags:
        layout.add_facts({"label": "Tags", "value": ", ".join(application.tags)})
    links = []
    for label, url in (
        ("Website", application.website_url),
        ("Documentation", application.docs_url),
        ("Support website", application.support_url),
    ):
        if url:
            links.append({"label": label, "url": url})
    support = application.support_server
    if support is not None:
        links.append({"label": "Join support", "url": support.join_url})
    if links:
        layout.add_actions(*links)
    return layout


async def main() -> None:
    async with Client(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
    ) as client:
        application = await client.get_application()
        preview = message_payload(profile_layout(application))
        print(json.dumps(preview, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
