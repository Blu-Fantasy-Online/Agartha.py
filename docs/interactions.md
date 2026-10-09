# Replies, menus, and forms

`Interaction` provides the response methods for a command, button, menu, autocomplete request, or form submission. Acknowledge within **three seconds**. After a confirmed acknowledgement, the response token permits follow-up operations for **15 minutes**.

## Reply directly in chat

```python
from agartha import Interaction


@bot.command(name="status", description="Check application status")
async def status(interaction: Interaction) -> None:
    await interaction.respond("Everything is ready.", ephemeral=True)
```

`ephemeral=True` makes the reply visible only to the invoking account in that channel. Omit it for a public chat reply. A command does not open a form unless your handler requests one.

Messages suppress mention alerts by default. Reference a user or bot with `<@PUBLIC_ID>` and a role with `<@&PUBLIC_ID>`, using its 18-digit public ID as a string. Chat presents the reference with the current name. `<@!PUBLIC_ID>` is also accepted as a user/bot reference. Mention tokens do not grant notification authority.

## Explicit mention alerts

To notify specific recipients, include their public IDs in `allowed_mentions`. Only references in the message's `content` can trigger these alerts. Text inside embeds, message layouts, or component labels does not trigger a mention alert.

```python
from agartha import allowed_mentions, mention_user, public_id

member_id = public_id("100000000000000081")
await interaction.respond(
    f"Your report is ready, {mention_user(member_id)}.",
    allowed_mentions=allowed_mentions(users=[member_id]),
)
```

| `allowed_mentions` field | Accepted value |
| --- | --- |
| `parse` | Omitted or an empty list; automatic parsing is unavailable |
| `users` | Omitted or a list of up to 20 unique public user/bot IDs |
| `roles` | Omitted or a list of up to five unique public role IDs |
| `replied_user` | Omitted or `false`; replies do not automatically notify their author |

`mention_user(id)`, `mention_role(id)`, and `allowed_mentions(users=(), roles=())` require **Agartha.py 0.5.1 or newer**. The first two create references; `allowed_mentions` creates the explicit notification policy. You can also pass the same fields as a dictionary.

The server checks each reference against the current visible server members, installed bots, and server roles. To opt in to a role alert, the role must be mentionable, or the bot must have the server's `mention_roles` permission. A display-only role reference needs no alert permission. The server's default/everyone role cannot be an alert recipient. Listing a recipient does not bypass channel access or their notification preferences. Bot references display the bot's name; they do not generate an account notification for a person. `@everyone` and `@here` are unavailable to bots.

The same policy applies to `Client.create_message`, message edits, initial interaction replies, source updates, and follow-up messages. Edits and source updates do not resend mention alerts. Ephemeral replies remain visible only to the invoker and produce no mention alerts. For an informational post, omit `allowed_mentions` and use ordinary names in your message or card.

Only public-ID mention tokens are accepted. A complete malformed reference is rejected; an unfinished `<@` remains ordinary text. The SDK and API validate message references before processing a mutation.

For rich cards, use `Embed` and `embed_payloads(...)` with `respond`, `edit_original`, or `followup`. See [rich embeds](embeds.md) for fields, media, attribution, and complete message limits. For provider-backed text replies, see [Build an AI bot](ai-bots.md).

Use `MessageLayout` with the same `embeds` argument to compose sections, galleries, facts, progress, expandable details, and placed actions. Callback placements reference the message's canonical components, so existing button/menu handlers and source updates work unchanged. See [Message layouts](message-layouts.md) for the builder and placement rules.

## Long work and follow-ups

Defer before calling a slow service, then update the original reply:

```python
@bot.command(name="report", description="Prepare a report")
async def report(interaction: Interaction) -> None:
    await interaction.defer(ephemeral=True)
    application = await interaction.client.get_application()
    await interaction.edit_original(f"Report ready for {application.name}.")
    extra = await interaction.followup("A separate note.", flags=64)
    await interaction.edit_followup(extra["id"], "Updated separate note.")
```

`followup(...)` returns a reply dictionary with an `id`. Use that ID to read, edit, or remove that specific reply. `edit_original(...)` always targets the original response; changing a follow-up does not replace the original.

| Method | Purpose |
| --- | --- |
| `respond(content=None, *, ephemeral=False, **data)` | Initial chat response |
| `defer(*, ephemeral=False)` | Acknowledge and show a pending chat response |
| `original_response()` | Read the original reply dictionary |
| `edit_original(content=None, **data)` | Complete a defer or edit the original reply |
| `delete_original()` | Remove the original reply |
| `followup(content=None, **data)` | Create a separate reply dictionary |
| `get_followup(message_id)` | Read one follow-up dictionary |
| `edit_followup(message_id, content=None, **data)` | Edit one follow-up |
| `delete_followup(message_id)` | Remove one follow-up |

Use `flags=64` for a private follow-up. Initial-response methods can be attempted only once. If delivery becomes uncertain, do not send a second acknowledgement blindly; see [error handling](errors-and-limits.md).

## Buttons and source updates

Components remain in the chat reply. Clicking a component delivers a new interaction to its registered custom ID.

```python
from agartha import action_row, button


@bot.command(name="panel", description="Show a status panel")
async def panel(interaction: Interaction) -> None:
    await interaction.respond(
        "Ready to refresh.",
        ephemeral=True,
        components=[action_row(button("panel:refresh", "Refresh"))],
    )


@bot.component("panel:refresh")
async def refresh_panel(interaction: Interaction) -> None:
    await interaction.defer_update()
    await interaction.edit_original("Refreshed.", components=[])
```

`update(content=None, **data)` immediately changes the component's source reply. `defer_update()` acknowledges a longer source update without adding another pending reply. Both require a valid source-linked component or form submission. They cannot update an unrelated message.

Up to five action rows are allowed. A row contains up to five buttons or one select. Callback button styles are `1` primary, `2` secondary, `3` success, and `4` danger. `disabled=True` disables a button. The `button` builder creates callback buttons; it does not create URL buttons.

## String and resource menus

```python
from agartha import entity_select, option, string_select


@bot.command(name="choose", description="Choose an action")
async def choose(interaction: Interaction) -> None:
    await interaction.respond(
        "Choose a topic or member.",
        ephemeral=True,
        components=[
            action_row(string_select("choose:topic", [
                option("Commands", "commands"),
                option("Forms", "forms"),
            ], placeholder="Topic")),
            action_row(entity_select("choose:member", 5, placeholder="Member")),
        ],
    )


@bot.component("choose:topic")
async def choose_topic(interaction: Interaction) -> None:
    await interaction.respond(
        f"Selected topic: {interaction.values[0]}", ephemeral=True
    )


@bot.component("choose:member")
async def choose_member(interaction: Interaction) -> None:
    await interaction.defer(ephemeral=True)
    member = await interaction.client.get_member(
        interaction.raw["server_id"], interaction.values[0]
    )
    name = member.raw.get("display_name") or member.raw.get("username")
    await interaction.edit_original(name or "Member name is unavailable.")
```

`interaction.values` returns a list of strings. Entity select types are `5` user, `6` role, `7` mentionable, and `8` channel. Their values are resource ID strings; their pickers display current server names. Channel selectors can set `channel_types`. Selects support `min_values`, `max_values`, `placeholder`, and `disabled`; a string select accepts up to 25 options.

## Open and receive a form

A command or component can request a form. Forms open because the bot calls `send_modal`, not because a command has been selected.

```python
from agartha import checkbox, label, text_input


@bot.command(name="feedback", description="Send private feedback")
async def feedback(interaction: Interaction) -> None:
    await interaction.send_modal("feedback:submit", "Feedback", [
        label("Your feedback", text_input("text", style=2, max_length=500)),
        label("Allow a follow-up", checkbox("follow_up")),
    ])


@bot.modal("feedback:submit")
async def receive_feedback(interaction: Interaction) -> None:
    values = interaction.form_values
    await interaction.respond(
        f"Feedback received: {values['text']}", ephemeral=True
    )
```

`interaction.form_values` is a dictionary keyed by each field's custom ID. Text is a string, multi-select/checkbox-group values are lists, a single checkbox is a boolean, and an optional unselected radio can be `None`.

A form contains one to five `label(...)` fields. Field IDs must be unique; titles and labels are at most 45 characters. Text fields allow up to 4,000 characters. A submission is consumed once and remains subject to user, channel, permission, and expiry checks. Submitted form JSON is limited to 24,000 UTF-8 bytes.

## Form field reference

| Builder | Main arguments and behavior |
| --- | --- |
| `label(text, component, description=None)` | Wrap one field with a human-readable label; description is optional |
| `text_input(custom_id, style=1, required=True, min_length=0, max_length=4000, value=None, placeholder=None, label=None)` | `style=1` short or `2` paragraph; wrap in a modern label |
| `string_select(custom_id, options, min_values=1, max_values=1, placeholder=None, disabled=False, required=None)` | Up to 25 unique option values |
| `entity_select(custom_id, kind, min_values=1, max_values=1, placeholder=None, disabled=False, required=None, channel_types=None)` | User/role/mentionable/channel choices; at most 25 selected values |
| `radio_group(custom_id, options, required=True)` | Two to ten options; at most one default |
| `checkbox_group(custom_id, options, min_values=1, max_values=None, required=True)` | One to ten options; `max_values=None` uses the option count |
| `checkbox(custom_id, default=False)` | One boolean; cannot require the user to check it |
| `file_upload(custom_id, min_values=1, max_values=1, required=True, file_types=None)` | One to ten files; optional fields use `required=False, min_values=0` |
| `option(label, value, description=None, default=False)` | A reusable select/radio/checkbox-group choice |
| `modal(custom_id, title, components)` | Build a form dictionary; `send_modal` calls this for you |

Optional builder parameters after the positional arguments are keyword-only. For optional select groups, use `required=False, min_values=0`. File filters can use `"image"`, `"video"`, `"audio"`, or extensions such as `".txt"` and `".pdf"`.

```python
from agartha import checkbox_group, file_upload, radio_group

fields = [
    label("Topic", radio_group("topic", [
        option("Commands", "commands"), option("Forms", "forms"),
    ])),
    label("Features", checkbox_group("features", [
        option("Buttons", "buttons"), option("Menus", "menus"),
    ], required=False, min_values=0)),
    label("Example file", file_upload(
        "files", required=False, min_values=0, file_types=[".txt", ".pdf"]
    )),
]
```

## Attachments

Users can supply a file through an attachment command option or a form upload. The returned ID refers to that submitted file. Use `download_attachment` to read its bytes.

```python
@bot.command(
    name="file-info",
    description="Check a submitted file",
    options=[{
        "name": "file",
        "description": "File to check",
        "type": 11,
        "required": True,
    }],
)
async def file_info(interaction: Interaction, file: str) -> None:
    await interaction.defer(ephemeral=True)
    metadata = interaction.resolved_attachments[file]
    data = await interaction.client.download_attachment(file)
    await interaction.edit_original(
        f"Received {metadata['filename']}: {len(data)} bytes."
    )
```

For a form upload, read the list of attachment IDs from `interaction.form_values["files"]`, then look up metadata in `interaction.resolved_attachments`. `attachment_reference(attachment_id)` returns `{"id": attachment_id}` when another supported payload needs a reference; it does not upload a file.

Downloads use Bot authentication on the configured API. Access is tied to the submitted interaction and current permissions. The per-file limit is 25 MiB, with account/server storage quotas also applied. The SDK validates download type and size. Allowed download MIME types cover JPEG/PNG/WebP/GIF, MP4/WebM, MP3/OGG/WAV, PDF, and plain text. General bot uploads are not available in native v1.

## Interaction properties and response types

| Property | Shape |
| --- | --- |
| `id` | Interaction ID string |
| `kind` | `2` command, `3` component, `4` autocomplete, or `5` form submission |
| `data` | Command/component/form data dictionary |
| `command_path` | Empty tuple or subcommand/group path tuple |
| `values` | Component selection string list |
| `form_values` | Flattened form values dictionary |
| `resolved_attachments` | Attachment metadata dictionaries keyed by attachment ID |
| `raw` | Delivered interaction dictionary, including application/server/channel references |
| `responded` | Whether an initial acknowledgement has been attempted |

| SDK method | Callback type | Valid input |
| --- | --- | --- |
| `respond` | `4` | Command, component, or form submit |
| `defer` | `5` | Command, component, or form submit |
| `defer_update` | `6` | Source-linked component or form submit |
| `update` | `7` | Source-linked component or form submit |
| `autocomplete(choices)` | `8` | Autocomplete only |
| `send_modal(custom_id, title, components)` | `9` | Command or component |

Do not log response tokens or full interaction URLs. Keep handler work async so other events can continue while a command runs.
