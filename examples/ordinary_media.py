"""Send an ordinary attachment in an explicitly selected test channel."""

import asyncio
import os
from pathlib import Path

from agartha import Client


async def main() -> None:
    path = Path(os.environ["AGARTHA_TEST_MEDIA_FILE"])
    async with Client(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
    ) as client:
        attachment = await client.upload_attachment(
            os.environ["AGARTHA_TEST_CHANNEL_ID"], await asyncio.to_thread(path.read_bytes),
            filename=path.name, content_type=os.environ["AGARTHA_TEST_MEDIA_TYPE"],
        )
        message = await client.create_message(
            os.environ["AGARTHA_TEST_CHANNEL_ID"], content="Media example",
            attachments=[attachment.reference()], embeds=[],
        )
        print("Sent", attachment.filename, "as ordinary chat media", message.id)


if __name__ == "__main__":
    asyncio.run(main())
