# Application commands

Users invoke commands with `/` in chat, **+ → Use Apps**, or an eligible user/message context menu. Agartha.py dispatches each invocation to an async handler.

The snippets on this page extend the `bot` created in the [quick start](quick-start.md). Sync after adding or changing definitions.

## Slash commands and options

```python
from agartha import Interaction


@bot.command(
    name="echo",
    description="Repeat a short message privately",
    options=[{
        "name": "text",
        "description": "The message to repeat",
        "type": 3,
        "required": True,
        "max_length": 500,
    }],
)
async def echo(interaction: Interaction, text: str) -> None:
    await interaction.respond(text, ephemeral=True)
```

Option names become handler keyword arguments. A missing optional option is omitted; give its handler argument a default. Put required options before optional options.

```python
@bot.command(
    name="greet",
    description="Choose a greeting",
    options=[{
        "name": "style",
        "description": "Greeting style",
        "type": 3,
        "choices": [
            {"name": "Friendly", "value": "friendly"},
            {"name": "Formal", "value": "formal"},
        ],
    }],
)
async def greet(interaction: Interaction, style: str = "friendly") -> None:
    text = "Welcome!" if style == "friendly" else "Good day."
    await interaction.respond(text)
```

| Option type | Value passed to your handler |
| --- | --- |
| `3` String | `str` |
| `4` Integer | `int` |
| `5` Boolean | `bool` |
| `6` User | User ID string |
| `7` Channel | Channel ID string |
| `8` Role | Role ID string |
| `9` Mentionable | User or role ID string |
| `10` Number | Numeric value |
| `11` Attachment | Submitted attachment ID string |

Resource options use server-aware pickers. Resolve labels from `interaction.data["resolved"]` or the [resource methods](resources.md); display a name rather than the selected ID. Attachment options use the [authenticated download method](interactions.md#attachments).

Slash names contain 1–32 lowercase letters, digits, underscores, or hyphens. Descriptions contain 1–100 characters. A level can contain at most 25 options or choices. String options can set `min_length`/`max_length`; numeric options can set `min_value`/`max_value`. A channel option can provide `channel_types`. Keep option definitions consistent with their types.

## Subcommands and groups

Register the root first. A root has either ordinary options or subcommands; it cannot mix them. One group level is supported.

```python
@bot.command(name="tools", description="Useful tools")
async def tools(interaction: Interaction) -> None:
    await interaction.respond("Choose a tools subcommand.", ephemeral=True)


@bot.subcommand(
    "tools",
    group="text",
    group_description="Text tools",
    name="echo",
    description="Repeat text",
    options=[{
        "name": "text",
        "description": "Text to repeat",
        "type": 3,
        "required": True,
        "autocomplete": True,
    }],
)
async def tools_echo(interaction: Interaction, text: str) -> None:
    await interaction.respond(text, ephemeral=True)
```

This defines `/tools text echo`. Omit `group` for `/tools echo`. `interaction.command_path` is `("text", "echo")` for the grouped invocation, and leaf values are passed as ordinary keyword arguments.

## Autocomplete

Autocomplete is available for string, integer, and number options. Set `autocomplete=True` in the option definition and register a matching command, path, and option handler.

```python
@bot.autocomplete("tools", "text", path=("text", "echo"))
async def suggest_text(interaction: Interaction, focused: str) -> list[dict]:
    suggestions = ["Hello", "Welcome", "Good evening"]
    return [
        {"name": text, "value": text}
        for text in suggestions
        if text.lower().startswith(focused.lower())
    ][:25]
```

The handler receives the focused value and any other supplied leaf options as keywords. Return up to 25 `{"name": ..., "value": ...}` choices, or call `await interaction.autocomplete(choices)` yourself. Numeric choices must match the option's integer/number type. Choice names and string values are at most 100 characters.

Autocomplete has its own initial response. Do not send a chat reply, defer, or open a form from an autocomplete interaction. Choices help users type an option; the final invocation still receives validation.

## User and message actions

Context command names can contain spaces and capitals. Type `2` targets a user; type `3` targets a message. The handler receives `(interaction, target_id)`.

```python
@bot.context_command(name="View member", type=2)
async def view_member(interaction: Interaction, target_id: str) -> None:
    await interaction.defer(ephemeral=True)
    member = await interaction.client.get_member(
        interaction.raw["server_id"], target_id
    )
    name = member.raw.get("username") or member.raw.get("display_name")
    await interaction.edit_original(
        f"Member: {name}" if name else "Member name is unavailable."
    )


@bot.context_command(name="Summarize message", type=3)
async def summarize_message(interaction: Interaction, target_id: str) -> None:
    await interaction.defer(ephemeral=True)
    message = await interaction.client.get_message(
        interaction.raw["channel_id"], target_id
    )
    await interaction.edit_original(
        message.content[:500] or "Message content is unavailable."
    )
```

The message action can read only content the bot is allowed to view. Reading a human message body requires approved message-content access.

## Permissions and registration

Use native permission names in `default_permissions` to limit who can invoke a command:

```python
@bot.command(
    name="settings",
    description="View application settings",
    default_permissions=["manage_servers"],
)
async def settings(interaction: Interaction) -> None:
    await interaction.respond("Settings are available to server managers.", ephemeral=True)
```

Invocation permissions do not expand the bot's installed permissions. Your later API call must still be authorized for the resource it changes.

| Call | Result |
| --- | --- |
| `await bot.sync_commands(server_id=server_id)` | Replace this app's test/server command set |
| `await bot.sync_commands()` | Replace this app's global command set |
| `await bot.client.list_commands(server_id=server_id)` | Read server definitions |
| `await bot.client.list_commands()` | Read global definitions |
| `await bot.client.replace_commands(definitions, server_id=server_id)` | Replace explicit definitions without decorators |

Server definitions override matching global definitions. Each scope supports up to 100 slash commands, 15 user actions, and 15 message actions. A server permits up to 200 new command creations per day. Editing an existing identity is not a new command creation. Synchronization is an explicit deployment action and does not happen at Gateway startup.

## Decorator reference

```text
Bot.command(*, name, description, options=None, **fields)
Bot.subcommand(command, *, name, description, group=None,
               group_description=None, options=None)
Bot.autocomplete(command, option, *, path=())
Bot.context_command(*, name, type=2)
Bot.component(custom_id)
Bot.modal(custom_id)
Bot.event(async_callback)
```

Handlers must be async. Command names, subcommand paths, context name/type pairs, and component/form custom IDs must be unique in their respective registrations. Component and form handlers match the **exact** custom ID; wildcard or prefix dispatch is not built in.
