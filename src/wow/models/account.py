"""Models for the Account Profile API.

Blizzard has not announced or documented a Forever profile API. This shape comes from community probing
(https://mhuijskens.com/WoWForever/Api/), not from a recorded live response: it needs a user token this package
cannot obtain on its own.
"""

import re

from wow.models._common import Document, IdName, Link, Model, Ref, TypedName

__all__ = ["AccountCharacter", "AccountProfile", "WowAccount"]

_PROTECTED_CHARACTER_RE = re.compile(r"/protected-character/(\d+)-\d+(?:[?/]|$)")


class AccountCharacter(Model):
    """One character on a WoW Forever account.

    Shape from community probing; Blizzard has not documented it. Forever characters carry a ``surname`` alongside
    their first ``name``, and omit the ``realm`` field retail and Classic characters have; the realm only shows up
    in :attr:`protected_character`'s link, which :attr:`realm_id` parses.
    """

    character: Link
    protected_character: Link
    name: str
    surname: str
    id: int
    playable_class: IdName
    playable_race: IdName
    gender: TypedName
    faction: TypedName
    level: int
    realm: Ref | None = None

    @property
    def realm_id(self) -> int | None:
        """The realm id parsed from :attr:`protected_character`'s link, or ``None`` if it cannot be parsed."""
        match = _PROTECTED_CHARACTER_RE.search(self.protected_character.href)
        return int(match.group(1)) if match else None


class WowAccount(Model):
    """One Battle.net account's WoW Forever characters.

    Shape from community probing; Blizzard has not documented it.
    """

    id: int
    characters: tuple[AccountCharacter, ...]


class AccountProfile(Document):
    """The authenticated user's account profile: every linked account's Forever characters.

    Shape from community probing; Blizzard has not documented it.
    """

    wow_accounts: tuple[WowAccount, ...]
