"""Build a public mention reply; the standalone preview does not post a message."""

import json

from agartha import Interaction, allowed_mentions, mention_role, mention_user


async def report_ready(interaction: Interaction, member_id: str) -> None:
    """Call from your command handler with an authorized current member's public ID."""
    await interaction.respond(
        f"Your report is ready, {mention_user(member_id)}.",
        allowed_mentions=allowed_mentions(users=[member_id]),
    )


if __name__ == "__main__":
    user = "100000000000000081"
    role = "100000000000000083"
    print(json.dumps({
        "content": f"Report ready for {mention_user(user)}. Team: {mention_role(role)}.",
        # The role reference displays its name; this policy only opts in to the user alert.
        "allowed_mentions": allowed_mentions(users=[user]),
    }, indent=2))
