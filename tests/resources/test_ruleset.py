from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_ruleset(client: Client) -> None:
    index = client.rulesets.index()

    assert sorted(ruleset.id for ruleset in index.rulesets) == [1, 2, 3, 15]


def test_get_reads_name_and_status(client: Client) -> None:
    pvp = client.rulesets.get(1)

    assert pvp.name == "PvP"
    assert pvp.status.type == "UP"
