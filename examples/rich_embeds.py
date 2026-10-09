"""A developer-hosted rich card command with explicit command synchronization."""

import argparse
import asyncio
import os
from datetime import UTC, datetime

from agartha import Bot, Embed, Intents, Interaction, embed_payloads


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-commands", action="store_true")
    options = parser.parse_args()
    bot = Bot(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
        intents=Intents.SERVERS,
    )

    @bot.command(name="status", description="Show a rich application status card")
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

    try:
        if options.sync_commands:
            await bot.sync_commands(server_id=os.environ["AGARTHA_TEST_SERVER_ID"])
        await bot.start()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
