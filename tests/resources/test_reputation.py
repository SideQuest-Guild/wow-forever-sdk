from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_faction_index_lists_factions_and_root_factions(client: Client) -> None:
    index = client.reputation_factions.index()

    assert len(index.factions) == 56
    assert index.factions[0].name == "Horde Forces"
    assert len(index.root_factions) == 35
    assert index.root_factions[0].name == "Horde Forces"


def test_faction_get_reads_faction_details(client: Client) -> None:
    faction = client.reputation_factions.get(892)

    assert faction.name == "Horde Forces"
    assert faction.is_header is True
    assert faction.player_faction is not None
    assert faction.player_faction.type == "HORDE"
    assert faction.player_faction.name == "Horde"
    assert faction.reputation_tiers.id == 0
    assert [sub.name for sub in faction.factions] == [
        "The Defilers",
        "Frostwolf Clan",
        "Warsong Outriders",
        "Darkspear Raiders",
    ]


def test_tiers_index_lists_tier_sets(client: Client) -> None:
    index = client.reputation_tiers.index()

    assert len(index.reputation_tiers) == 1
    assert index.reputation_tiers[0].id == 0


def test_tiers_get_reads_standing_levels(client: Client) -> None:
    tiers = client.reputation_tiers.get(0)

    assert len(tiers.tiers) == 8
    assert tiers.tiers[0].name == "Hated"
    assert tiers.tiers[0].min_value == -42000
    assert tiers.tiers[0].max_value == -6000
    assert tiers.tiers[-1].name == "Exalted"
    assert tiers.tiers[-1].max_value == 43000
