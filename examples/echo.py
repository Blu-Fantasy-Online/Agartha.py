"""Explicit development echo bot; never registers commands implicitly."""

import argparse
import asyncio
import os

from agartha import Bot, Intents, Interaction


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-commands", action="store_true")
    options = parser.parse_args()
    bot = Bot(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
        intents=Intents.SERVERS,
    )

    @bot.command(
        name="echo",
        description="Echo text back privately",
        options=[{"type": 3, "name": "text", "description": "Text to echo", "required": True}],
    )
    async def echo(interaction: Interaction, text: str) -> None:
        await interaction.respond(text, ephemeral=True)

    @bot.event
    async def on_ready(payload: dict[str, object]) -> None:
        print("Agartha echo application connected.")

    try:
        if options.sync_commands:
            await bot.sync_commands()
        await bot.start()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
