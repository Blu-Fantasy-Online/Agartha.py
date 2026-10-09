# Account authorization

Use `OAuthClient` when a user chooses to grant your application access to their account information. OAuth is separate from Bot authentication and server installation. Request only the read scopes needed for your feature.

## Register a callback

Set an exact HTTPS callback URI in the application settings, for example `https://example.com/agartha/callback`. Configure confidential applications with their OAuth client secret in server-side hosting. The application ID is its OAuth client ID.

The consent endpoint is `https://blufantasy.online/agartha/developers/authorize`. `OAuthClient.api_url` is the API **origin**, `https://agartha-api.blufantasy.online`, without `/api/v1`.

| Scope | SDK method |
| --- | --- |
| `identify` | `get_user(access_token)` |
| `servers` | `get_servers(access_token)` |
| `servers.members.read` | `get_member(access_token, server_id)` for the consenting user's membership |

These scopes do not install a bot or grant member administration.

## Build the consent link

Create an unpredictable state value and a PKCE verifier for each authorization attempt. Store them in the user's server-side application session until the callback arrives.

```python
import secrets

from agartha import authorization_url, pkce_verifier

verifier = pkce_verifier()
state = secrets.token_urlsafe(32)
consent_url = authorization_url(
    "https://blufantasy.online/agartha/developers/authorize",
    client_id="100000000000000086",
    redirect_uri="https://example.com/agartha/callback",
    state=state,
    code_verifier=verifier,
    scopes=("identify", "servers"),
)
```

Redirect the user to `consent_url`. Agartha shows the application's requested scopes, and the user can approve or deny them. Your application owns session storage and its callback route.

## Exchange the returned code

Compare the callback's state to the saved state with a constant-time check before exchanging the code. Use the saved verifier and exact registered callback URI.

```python
from agartha import OAuthClient


async def exchange_code(
    code: str, returned_state: str, saved_state: str, saved_verifier: str,
    client_id: str, client_secret: str | None = None,
):
    if not secrets.compare_digest(returned_state, saved_state):
        raise ValueError("Authorization state did not match this session.")
    async with OAuthClient(
        client_id,
        api_url="https://agartha-api.blufantasy.online",
        client_secret=client_secret,
    ) as oauth:
        tokens = await oauth.exchange(
            code,
            redirect_uri="https://example.com/agartha/callback",
            code_verifier=saved_verifier,
        )
        user = await oauth.get_user(tokens.access_token)
        return tokens, user
```

`OAuthTokens` contains `access_token`, `refresh_token`, `expires_in`, and `scopes`. Its representation hides the tokens. Store tokens securely; the SDK does not store them for you.

Authorization codes expire after two minutes. Access tokens last 15 minutes; refresh tokens last up to 30 days. Use the returned `expires_in` for the current token's actual deadline.

## Read, refresh, and revoke

```python
async def read_authorized_servers(oauth: OAuthClient, tokens):
    servers = await oauth.get_servers(tokens.access_token)
    return [server.name for server in servers]


async def rotate_tokens(oauth: OAuthClient, tokens):
    replacement = await oauth.refresh(tokens.refresh_token)
    return replacement


async def disconnect(oauth: OAuthClient, tokens) -> None:
    await oauth.revoke(tokens.access_token)
```

Refresh returns a new token pair and consumes the previous refresh token. Save both replacement values together. Replaying a consumed refresh can revoke the authorization family. User revocation, client-secret rotation, application status changes, or lost consent can also end access; send the user through consent again when needed.

OAuth requests are not automatically retried. Do not repeat an uncertain exchange/refresh blindly. `OAuthError` provides a safe HTTP status and recognized error code, such as `invalid_grant`, `access_denied`, `invalid_token`, or `insufficient_scope`.

## Method reference

```text
pkce_verifier() -> str
authorization_url(endpoint, *, client_id, redirect_uri, state,
                  code_verifier, scopes=("identify",)) -> str
OAuthClient(client_id, *, api_url, client_secret=None, timeout=30)
await oauth.exchange(code, *, redirect_uri, code_verifier) -> OAuthTokens
await oauth.refresh(refresh_token) -> OAuthTokens
await oauth.revoke(token) -> None
await oauth.get_user(access_token) -> Resource
await oauth.get_servers(access_token) -> list[Server]
await oauth.get_member(access_token, server_id) -> Member
await oauth.close() -> None
```

User reads send `Authorization: Bearer ...`. `Client` and `Bot` send Bot credentials. Do not interchange these tokens. Use `.raw` to access the returned user's username/display name, and the account's 18-digit string ID for resource references.
