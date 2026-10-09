"""Read-only API smoke check by default; writes require an explicit development flag."""

import argparse
import asyncio
import os
import uuid

from agartha import Client


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel-id")
    parser.add_argument("--write-checks", action="store_true")
    options = parser.parse_args()
    if options.write_checks and not options.channel_id:
        parser.error("--write-checks requires a development --channel-id")
    async with Client(
        os.environ["AGARTHA_BOT_TOKEN"], base_url=os.environ["AGARTHA_API_BASE_URL"]
    ) as client:
        app = await client.get_application()
        commands = await client.list_commands()
        await client.get_gateway()
        servers = await client.list_servers()
        channel_count = 0
        for server in servers:
            await client.get_server(server.public_id or server.id)
            await client.list_members(server.id)
            await client.list_roles(server.id)
            await client.list_audit_logs(server.id)
            for channel in await client.list_channels(server.id):
                channel_count += 1
                await client.get_channel(channel.id)
                for message in (await client.list_messages(channel.id, limit=1))[:1]:
                    await client.get_message(channel.id, message.id)
        if options.write_checks:
            message = await client.create_message(
                options.channel_id, content="Agartha SDK smoke test", nonce=str(uuid.uuid4())
            )
            try:
                await client.get_message(options.channel_id, message.id)
                await client.edit_message(
                    options.channel_id, message.id, content="Agartha SDK smoke test updated"
                )
                await client.replace_commands(commands)
            finally:
                await client.delete_message(options.channel_id, message.id)
        print(f"OK: application {app.id}; {len(servers)} servers; {channel_count} channels.")


if __name__ == "__main__":
    asyncio.run(main())
