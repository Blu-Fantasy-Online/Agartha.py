"""Developer-hosted native layouts using existing command and action handlers."""

import argparse
import asyncio
import os

from agartha import Bot, Intents, Interaction, MessageLayout, action_row, button, message_payload


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-commands", action="store_true")
    options = parser.parse_args()
    bot = Bot(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
        intents=Intents.SERVERS,
    )

    @bot.command(name="launch", description="Explore a native community launch message")
    async def launch(interaction: Interaction) -> None:
        layout = (
            MessageLayout(accent=0x21C3B2)
            .add_heading("Community launch", level=1)
            .add_section("A new season starts Friday.", title="Explore what is coming")
            .add_facts({"label": "Starts", "value": "Friday · 6:00 PM"},
                       {"label": "Where", "value": "Community lounge"}, columns=2)
            .add_divider()
            .add_progress("Launch preparations", 8, 10, unit="tasks")
            .add_callout("Everyone is welcome.", tone="success")
            .add_details("What to bring", "Bring your ideas and a friend.")
            .add_actions({"custom_id": "launch:join"},
                         {"label": "Developer guide", "url": "https://blufantasy.online/"
                          "agartha/developers/docs?doc=embeds"})
        )
        await interaction.respond(**message_payload(
            layout, components=[action_row(button("launch:join", "Join the launch"))],
        ))

    @bot.component("launch:join")
    async def join(interaction: Interaction) -> None:
        # Permission-sensitive mutations must use documented, server-authorized API calls.
        layout = (MessageLayout(accent=0x21C3B2)
                  .add_heading("You are welcome")
                  .add_callout("See you in the community lounge on Friday.", tone="success"))
        await interaction.respond(ephemeral=True, **message_payload(layout))

    try:
        if options.sync_commands:
            await bot.sync_commands(server_id=os.environ["AGARTHA_TEST_SERVER_ID"])
        await bot.start()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
