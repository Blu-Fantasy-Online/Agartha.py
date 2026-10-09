# Files and expressions in chat

Agartha.py **0.5.2** adds ordinary file uploads and typed attachments. Upload bytes, attach their public reference, and send them as normal chat media. Images, animated GIFs, video, audio, documents, and text files do not need an embed or message layout.

## Upload and send

```python
from pathlib import Path

image = await client.upload_attachment(
    channel_id,
    Path("community.gif").read_bytes(),
    filename="community.gif",
    content_type="image/gif",
    nonce="community-file-2026-10-09",
)
message = await client.create_message(
    channel_id,
    content="A community update from our team.",
    attachments=[image.reference()],
    embeds=[],
    nonce="community-message-2026-10-09",
)
```

An attachment-only message uses `content=""`, `attachments=[image.reference()]`, and `embeds=[]`. Uploads require an active installation with `view_channel`, `send_messages`, and `post_media` in the target channel. Text, media, and forum channels are supported; this ordinary media API does not accept encrypted server content.

The initial limit is **25 MiB per file**, with **ten attachments per bot message**. Supported content types are `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `video/mp4`, `video/webm`, `audio/mpeg`, `audio/ogg`, `audio/wav`, `application/pdf`, and `text/plain`. File signatures must match the declared type. SVG and HTML uploads are unavailable. Supply a filename, without a filesystem path.

Staged files expire after **24 hours** unless attached to a message. The server's media capacity and an application's pending upload allowance also apply. An attachment belongs to the application and channel that uploaded it; it cannot be reused in another channel or a second message. A same-payload create with the same message nonce returns its previous result. A stable upload nonce likewise lets a caller recover completed file metadata; a conflicting payload produces a conflict, and an unfinished upload must be reconciled before retrying.

## Read and edit

```python
message = await client.get_message(channel_id, message_id)
for attachment in message.attachments:
    print(attachment.filename, attachment.size, attachment.content_type)
    file_bytes = await client.download_attachment(attachment.id)

# Omission keeps the existing attachments.
await client.edit_message(channel_id, message.id, content="Updated caption")

# Retain selected files explicitly, or include new staged file references.
await client.edit_message(
    channel_id, message.id,
    attachments=[attachment.reference() for attachment in message.attachments],
)

# An empty list removes all attachments; leave a valid text/card/control message.
await client.edit_message(channel_id, message.id, content="Files removed", attachments=[])
```

`Message.attachments` is an immutable tuple of `Attachment` resources. Each exposes `id`, `filename`, `size`, `content_type`, `url`, `reference()`, and `raw`. Older responses without attachment metadata return an empty tuple. Removing files, archiving a message, or abandoning an upload schedules its bytes for cleanup.

Metadata for a human member's larger files remains readable, up to the platform's 20 GiB maximum. This initial bot media API uploads and downloads files up to 25 MiB. Check `attachment.size` before downloading; a larger file can remain part of the message without the bot fetching its bytes.

Download with `download_attachment(id)`, using your Bot credentials. The metadata URL is an authenticated API endpoint. Current channel visibility is checked on every download. Reading another author's attachments requires approved `Intents.MESSAGE_CONTENT`; the application's own visible messages remain readable without that privileged intent. Revoked access stops subsequent reads. The SDK does not fetch a caller-supplied media URL.

Uploads and attachment writes are supported by ordinary channel messages. Interaction attachment options and form submissions continue to use their existing [submitted attachment workflow](interactions.md#attachments); upload references are not accepted in interaction replies or follow-ups.

## Server emoji and stickers

Message content uses public expression references: `<:e:EXPRESSION_ID>` for an emoji, `<:a:EXPRESSION_ID>` for an animated emoji, and `<:s:EXPRESSION_ID>` for a sticker. Keep the 18-digit expression ID as a string. The referenced expression must be active in that message's server, or have an eligible portable delivery already referenced in a currently visible message in this channel. Reading a portable reference requires approved Message Content access unless it appears in the application's own visible message. This does not grant access to the expression's source server. Revoking its delivery eligibility or destination visibility stops subsequent reads.

```python
message = await client.get_message(channel_id, message_id)
for expression in message.expressions:
    print(expression.name, expression.kind)
    image_bytes = await client.download_expression(channel_id, expression.id)

await client.create_message(channel_id, content=f"Welcome <:e:{expression.id}>")
```

`Message.expressions` exposes `Expression` resources with `id`, `name`, `kind`, `url`, and `raw`. Its byte endpoint uses the current channel context and authenticated visibility. Normal Unicode emoji remain ordinary text. Custom expression reactions are a separate capability and are not introduced by this media API.

## HTTP methods

| Agartha.py call | API method and path |
| --- | --- |
| `upload_attachment(channel_id, bytes, filename=..., content_type=..., nonce=...)` | `POST /channels/{channel_id}/attachments` |
| `download_attachment(attachment_id)` | `GET /attachments/{attachment_id}` |
| `download_expression(channel_id, expression_id)` | `GET /channels/{channel_id}/expressions/{expression_id}/media` |

The upload uses multipart fields `payload_json` and `files[0]`. `payload_json` contains `filename`, `size`, `content_type`, and an optional `nonce`. A successful response contains `id`, `filename`, `size`, `content_type`, and `url`. Message create/edit accepts `attachments: [{"id": "ATTACHMENT_ID"}]`; omitted edits retain files, while `[]` removes them.

Only confirmed HTTP 429 responses retry automatically. The SDK recreates the multipart body for those retries. Other failures can represent uncertain delivery; use the documented nonce behavior to reconcile rather than blindly creating another upload or message.
