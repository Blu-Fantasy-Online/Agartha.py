# Build your first bot

This guide connects a bot to your test server and adds `/ping`. You need an approved developer account, an application, a bot token, and an installed test server.

## Install Agartha.py

Use **Python 3.12 or newer**. Download the [0.5.2 wheel](https://github.com/Blu-Fantasy-Online/Agartha.py/releases/download/v0.5.2/agartha_py-0.5.2-py3-none-any.whl), then run:

```text
python -m venv .venv
python -m pip install ./agartha_py-0.5.2-py3-none-any.whl
```

Activate your virtual environment before installing or running the bot: use `.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` on macOS/Linux. Official [GitHub releases](https://github.com/Blu-Fantasy-Online/Agartha.py/releases) and [SHA256 checksums](https://www.blufantasy.online/downloads/agartha/SHA256SUMS) are available. Install the published wheel until a public package registry release is announced. Agartha.py is proprietary; its [SDK license](https://github.com/Blu-Fantasy-Online/Agartha.py/blob/main/LICENSE) permits building your own bots while restricting redistribution and recreating the SDK or platform.

Set these environment values in your hosting configuration:

| Name | Value |
| --- | --- |
| `AGARTHA_BOT_TOKEN` | The bot token generated in your application's settings |
| `AGARTHA_API_BASE_URL` | `https://agartha-api.blufantasy.online/api/v1` |
| `AGARTHA_TEST_SERVER_ID` | Your test server's copied 18-digit ID |

Use the API address shown in the developer panel if your environment provides a different endpoint. Do not commit your token or print it in logs.

## Install the application

Open **Applications → your application → Install on a server**. Select your test server and approve the required permissions. The installing account needs **Manage Servers** and can grant only permissions it currently holds.

For this command, request basic server visibility. Add message permissions later if the bot will post outside an interaction. The application receives a managed bot role; server roles and channel overrides continue to control its access.

## Write the bot

Save this as `bot.py`:

```python
import argparse
import asyncio
import os

from agartha import Bot, Interaction, Intents

bot = Bot(
    os.environ["AGARTHA_BOT_TOKEN"],
    base_url=os.environ["AGARTHA_API_BASE_URL"],
    intents=Intents.SERVERS,
)


@bot.command(name="ping", description="Check whether the bot is connected")
async def ping(interaction: Interaction) -> None:
    await interaction.respond("Pong!", ephemeral=True)


@bot.event
async def on_ready(payload: dict) -> None:
    print("Agartha bot connected")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    try:
        if args.sync:
            await bot.sync_commands(
                server_id=os.environ["AGARTHA_TEST_SERVER_ID"]
            )
        await bot.start()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## Register and test

Run `python bot.py --sync` once to replace this application's commands in the test server and start the connection. Later starts can use `python bot.py` without replacing commands. Synchronization replaces the **whole command set in the chosen scope**, so register every command you want to keep before syncing.

In a standard chat channel, type `/ping`, select your application if another bot has the same command name, and press Enter. The reply appears in chat with **Only visible to you**. The **+ → Use Apps** picker offers the same command and returns to the composer to submit it.

A command runs directly from chat. A form appears only when your handler explicitly calls `interaction.send_modal(...)`.

## What happens in this example

`Bot` combines an authenticated `Client` with a `GatewayClient`. `@bot.command(...)` defines the command; `sync_commands(...)` registers its definition; the Gateway delivers the invocation to your async handler. `interaction.respond(...)` acknowledges and sends its reply.

Use `bot.run()` for a simple synchronous entry point, or `await bot.start()` inside an existing event loop. Always close the bot on shutdown. For requests without an event connection, use [Client directly](resources.md#client-lifecycle).

Next: add [options and subcommands](commands.md), then build [menus and forms](interactions.md).
