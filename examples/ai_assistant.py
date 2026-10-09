"""Developer-hosted /ask and /forget using your own Chat Completions-compatible provider."""

import argparse
import asyncio
import json
import os
from urllib.parse import urlsplit

import aiohttp

from agartha import AIAssistant, AIBusy, AIError, AIRequest, AISessionKey, Bot, Intents, Interaction


class HTTPChatProvider:
    """A text-only adapter. It never forwards Agartha credentials, IDs, or tool definitions."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        endpoint: str,
        api_key: str,
        model: str,
        max_completion_tokens: int = 512,
    ) -> None:
        url = urlsplit(endpoint)
        if (
            url.scheme != "https"
            or not url.hostname
            or url.username is not None
            or url.password is not None
            or "#" in endpoint
            or not endpoint.startswith("https://")
            or len(endpoint) > 2048
            or "\\" in endpoint
            or any(char.isspace() or ord(char) <= 32 or ord(char) == 127 for char in endpoint)
        ):
            raise ValueError(
                "Configure an HTTPS provider endpoint without credentials or fragments."
            )
        if not api_key or "\r" in api_key or "\n" in api_key or not model:
            raise ValueError("Configure your own provider key and model.")
        if type(max_completion_tokens) is not int or not 1 <= max_completion_tokens <= 4096:
            raise ValueError("Provider token limit is invalid.")
        self.session = session
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.max_completion_tokens = max_completion_tokens

    async def __call__(self, request: AIRequest) -> str:
        async with self.session.post(
            self.endpoint,
            headers={"Authorization": "Bearer " + self.api_key},
            json={
                "model": self.model,
                "messages": [
                    {"role": item.role, "content": item.content} for item in request.messages
                ],
                "max_completion_tokens": self.max_completion_tokens,
                "stream": False,
            },
            allow_redirects=False,
            timeout=aiohttp.ClientTimeout(total=25),
        ) as response:
            if response.status != 200 or response.content_type != "application/json":
                raise AIError("The AI provider request failed.")
            body = bytearray()
            async for chunk in response.content.iter_chunked(4096):
                body.extend(chunk)
                if len(body) > 65536:
                    raise AIError("The AI provider response is too large.")
            try:
                payload = json.loads(body)
                choices = payload["choices"]
                if not isinstance(choices, list) or len(choices) != 1:
                    raise ValueError
                message = choices[0]["message"]
                result = message["content"]
                if (
                    message.get("tool_calls")
                    or message.get("function_call")
                    or not isinstance(result, str)
                ):
                    raise ValueError
                return result
            except (ValueError, TypeError, KeyError, IndexError):
                raise AIError("The AI provider returned an unsupported text response.") from None


def create_bot(bot: Bot, assistant: AIAssistant) -> None:
    """Register handlers only; running and command synchronization are explicit."""

    @bot.command(
        name="ask",
        description="Ask this server's AI assistant privately",
        options=[
            {
                "type": 3,
                "name": "prompt",
                "description": "Your question (up to 2000 characters)",
                "required": True,
                "max_length": 2000,
            }
        ],
    )
    async def ask(interaction: Interaction, prompt: str) -> None:
        await interaction.defer(ephemeral=True)
        try:
            answer = await assistant.ask(AISessionKey.from_interaction(interaction), prompt)
        except AIBusy:
            answer = "The assistant is busy. Try again shortly."
        except AIError:
            answer = "The assistant could not answer this request. Try again later."
        except ValueError:
            answer = "Use a question of up to 2000 characters in a server channel."
        await interaction.edit_original(answer)

    @bot.command(name="forget", description="Clear your AI conversation in this channel")
    async def forget(interaction: Interaction) -> None:
        await interaction.defer(ephemeral=True)
        await assistant.clear(AISessionKey.from_interaction(interaction))
        await interaction.edit_original("Your conversation in this channel was cleared.")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-commands", action="store_true")
    options = parser.parse_args()
    bot = Bot(
        os.environ["AGARTHA_BOT_TOKEN"],
        base_url=os.environ["AGARTHA_API_BASE_URL"],
        intents=Intents.SERVERS,
    )
    async with aiohttp.ClientSession(trust_env=False) as transport:
        provider = HTTPChatProvider(
            transport,
            endpoint=os.environ["AI_PROVIDER_URL"],
            api_key=os.environ["AI_PROVIDER_KEY"],
            model=os.environ["AI_PROVIDER_MODEL"],
        )
        assistant = AIAssistant(
            provider,
            system_prompt=(
                "You are a helpful text assistant. Answer concisely in at most 1800 characters. "
                "You have no tools, server permissions, or access to other conversations."
            ),
        )
        create_bot(bot, assistant)
        try:
            if options.sync_commands:
                await bot.sync_commands(server_id=os.environ["AGARTHA_TEST_SERVER_ID"])
            await bot.start()
        finally:
            await assistant.close()
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
