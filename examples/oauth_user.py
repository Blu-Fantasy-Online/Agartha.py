"""Integrate these helpers with a protected web session and registered callback."""

import hmac
import secrets
from dataclasses import dataclass, field

from agartha import OAuthClient, OAuthTokens, authorization_url, pkce_verifier


@dataclass(frozen=True)
class PendingConsent:
    url: str
    state: str = field(repr=False)
    verifier: str = field(repr=False)


def begin_consent(
    client_id: str, authorization_endpoint: str, registered_callback: str
) -> PendingConsent:
    state, verifier = secrets.token_urlsafe(32), pkce_verifier()
    # Store state/verifier in the application's protected short-lived session;
    # redirect the browser to URL, and do not log the session contents.
    url = authorization_url(
        authorization_endpoint,
        client_id=client_id,
        redirect_uri=registered_callback,
        state=state,
        code_verifier=verifier,
        scopes=("identify", "servers"),
    )
    return PendingConsent(url, state, verifier)


async def complete_consent(
    client: OAuthClient,
    pending: PendingConsent,
    *,
    returned_state: str,
    code: str,
    registered_callback: str,
) -> OAuthTokens:
    # The redirect handler loads and consumes its pending protected session;
    # compare state before giving the code to the token endpoint.
    if not hmac.compare_digest(returned_state, pending.state):
        raise ValueError("OAuth callback state did not match the pending consent.")
    return await client.exchange(
        code, redirect_uri=registered_callback, code_verifier=pending.verifier
    )
