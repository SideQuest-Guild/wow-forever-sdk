from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_the_skyborne_races_alongside_the_originals(client: Client) -> None:
    index = client.playable_races.index()

    assert len(index.races) == 10
    assert index.races[0].id == 95
    assert index.races[0].name == "High Order Skyborne"
    assert index.races[1].id == 96
    assert index.races[1].name == "Windshaper Skyborne"


def test_get_reads_race_details(client: Client) -> None:
    race = client.playable_races.get(95)

    assert race.name == "High Order Skyborne"
    assert race.faction.type == "ALLIANCE"
    assert race.faction.name == "Alliance"
    assert race.is_allied_race is False
    assert race.is_selectable is True
    assert [cls.name for cls in race.playable_classes] == ["Warrior", "Druid", "Rogue", "Hunter", "Mage"]
    assert len(race.racial_spells) == 5
