# Build an AI bot

Run an AI application on your own server using Agartha.py and your chosen provider. `AIAssistant` supplies bounded text history and an async provider interface. You supply the provider connection, model, credentials, and hosting; requests use your provider account and quota.

## Application setup

1. Create an approved developer application and install it in a test server.
2. Run the bot with `Intents.SERVERS`. Slash-command prompts come from the invoking interaction, so this example does not need message-content or member access.
3. Store `AGARTHA_BOT_TOKEN` and provider credentials in your server's secret store or environment.
4. Register `/ask` and `/forget` explicitly, then run the Gateway client.
5. Tell users which provider handles their submitted prompts and set your application's data and cost policies.

The helper generates plain text. It does not execute model-proposed server actions or expose Agartha clients, bot tokens, interaction tokens, IDs, or tool definitions to a provider. Every reply still passes Agartha's current server authorization checks.

## A provider-neutral helper

An async provider receives `AIRequest` and returns one string. The request holds an immutable tuple of `AIMessage(role, content)` records and a `max_output_chars` limit. Roles are `system`, `user`, and `assistant`; application and user IDs remain in the local session key.

```python
from agartha import AIAssistant, AIRequest, AISessionKey, Interaction


async def provider(request: AIRequest) -> str:
    # Replace with your own async provider transport.
    # Send request.messages and return plain text within request.max_output_chars.
    return "Your provider adapter is ready."


assistant = AIAssistant(
    provider,
    system_prompt="Answer concisely. You provide text and have no server tools.",
    max_output_chars=1800,
)


@bot.command(
    name="ask",
    description="Ask your AI assistant privately",
    options=[{
        "name": "prompt", "description": "Your question", "type": 3,
        "required": True, "max_length": 2000,
    }],
)
async def ask(interaction: Interaction, prompt: str) -> None:
    await interaction.defer(ephemeral=True)
    key = AISessionKey.from_interaction(interaction)
    answer = await assistant.ask(key, prompt)
    await interaction.edit_original(answer)
```

This first provider is an offline stub. Replace it with your adapter to obtain model output. Defer within three seconds before contacting a provider; avoid blocking SDK event handlers. The SDK suppresses mentions in the generated reply.

## Runnable HTTP example

The source package includes `examples/ai_assistant.py`. It registers `/ask` and `/forget`, acknowledges privately, handles capacity/provider failures with safe text, and closes outstanding AI work during shutdown.

Configure these environment values on your bot host:

| Variable | Value |
| --- | --- |
| `AGARTHA_BOT_TOKEN` | This application's bot token |
| `AGARTHA_API_BASE_URL` | API endpoint supplied in the developer panel |
| `AGARTHA_TEST_SERVER_ID` | Your test server's 18-digit ID; needed only for explicit sync |
| `AI_PROVIDER_URL` | Your selected HTTPS Chat Completions endpoint |
| `AI_PROVIDER_KEY` | Your own provider account's API key |
| `AI_PROVIDER_MODEL` | Model available on that provider account |

From the source package directory:

```text
python examples/ai_assistant.py --sync-commands
```

The example sends a Chat Completions-compatible JSON request containing `model`, `messages`, `max_completion_tokens=512`, and `stream=false`. The provider must support those fields and return exactly one `choices[].message.content` string. Adapt `HTTPChatProvider` if your provider uses a different API. The model token limit and helper character limit are separate bounds. The [Chat Completions API reference](https://developers.openai.com/api/reference/resources/chat) documents this request/response convention.

The adapter uses an async `aiohttp` transport, a 25-second HTTP timeout, a 64 KiB response cap, and no redirects. It rejects tool/function-call responses. It forwards only the configured provider key and text messages. Provider errors are shown as generic failures without raw response text or credentials. Run on your own host; selecting an AI starter does not provision a model or shared BFO provider account.

## Scope, memory, and deletion

`AISessionKey(application_id, server_id, channel_id, user_id)` uses four 18-digit strings. `AISessionKey.from_interaction(interaction)` reads the delivered invocation's scope; do not substitute user-supplied command options. A different user, channel, server, or application starts a separate conversation. Concurrent questions in the same scope are serialized.

```python
@bot.command(name="forget", description="Clear your AI conversation in this channel")
async def forget(interaction: Interaction) -> None:
    await interaction.defer(ephemeral=True)
    await assistant.clear(AISessionKey.from_interaction(interaction))
    await interaction.edit_original("Your conversation in this channel was cleared.")
```

`clear` waits for that scope's in-flight request, then erases its text history. Other scopes retain their histories. History is held only in this bot process: restarting clears it; no shared persistence is created. Expired idle sessions are removed before the next question is accepted. Configure retention on your provider separately; clearing local history does not delete records held by another service.

Always close the helper in your application's shutdown path:

```python
async def run_bot() -> None:
    try:
        await bot.start()
    finally:
        await assistant.close()
        await bot.close()
```

`close()` cancels outstanding asks, erases local histories, and rejects new questions. Close the provider's transport separately, such as by using `async with aiohttp.ClientSession(...)` as the runnable example does. Providers must support asyncio cancellation and set their own transport deadlines.

## Capacity and error reference

All options after `provider` are keyword-only. `system_prompt` is required.

| Option | Default | Behavior |
| --- | --- | --- |
| `max_turns` | `6` | Retain at most six completed prompt/reply pairs |
| `max_context_chars` | `12000` | Bound combined system/history/current prompt text sent to the provider; oldest pairs are removed first |
| `max_prompt_chars` | `2000` | Reject longer or blank prompts before calling the provider |
| `max_output_chars` | `1800` | Reject empty, nontext, or longer output before storing or replying |
| `max_sessions` | `128` | Bound active/retained scopes; no active conversation is evicted to make space |
| `max_concurrency` | `4` | Bound all outstanding asks, including same-scope requests waiting for a turn |
| `timeout` | `30` seconds | Bound a question's provider work and wait for its scope lock |
| `idle_ttl` | `900` seconds | Expire idle scope history before the next question is accepted |

The context budget must fit the system prompt plus one maximum prompt and response. Character limits do not measure provider tokens or guarantee a spending limit; configure model output and provider billing limits in your adapter/account.

| Exception | Meaning |
| --- | --- |
| `AIBusy` | Request or session capacity is full; ask the user to retry later |
| `AIProviderTimeout` | The configured question deadline elapsed |
| `AIInvalidResponse` | Provider output was empty, nontext, or beyond the character cap |
| `AIProviderError` | Provider/transport failed; raw provider detail is suppressed |
| `AIError` | AI helper failure, including use after shutdown; all AI exceptions inherit it |
| `ValueError` | Invalid configuration, scope, or prompt |

Only successful replies enter history. A timeout, provider failure, cancelled request, or invalid output leaves the previous history intact. The helper does not retry provider calls automatically. For Agartha HTTP errors and permission changes, use the existing [error guide](errors-and-limits.md). To present generated text in a card, validate it through the [embed builder](embeds.md) before writing.
