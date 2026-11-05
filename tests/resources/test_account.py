from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_profile_sends_the_user_token_and_reads_characters(client: Client, battlenet: respx.MockRouter) -> None:
    user_client = client.with_options(access_token="user-token")

    profile = user_client.account.profile()

    assert profile.wow_accounts[0].id == 1234567
    character = profile.wow_accounts[0].characters[0]
    assert character.name == "Davina"
    assert character.surname == "Asaria"
    assert character.id == 716333
    assert character.playable_class.name == "Priest"
    assert character.playable_race.name == "Troll"
    assert character.gender.type == "FEMALE"
    assert character.faction.type == "HORDE"
    assert character.level == 1
    assert character.realm is None
    assert character.realm_id == 6921
    request = battlenet["api"].calls.last.request
    assert request.headers["Authorization"] == "Bearer user-token"
