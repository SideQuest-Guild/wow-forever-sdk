from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_get_reads_quest_details(client: Client) -> None:
    quest = client.quests.get(1)

    assert quest.title == 'The "Chow" Quest (123)aa'
    assert quest.area is not None
    assert quest.area.name == "Dustwallow Marsh"
    assert quest.rewards.experience == 550
    assert quest.rewards.items is not None
    assert quest.rewards.money is not None
    assert [item.item.name for item in quest.rewards.items.items] == [
        "Refreshing Spring Water",
        "Minor Healing Potion",
    ]
    assert quest.rewards.money.value == 225
    assert quest.rewards.money.units.gold == 0
    assert quest.rewards.money.units.silver == 2
    assert quest.rewards.money.units.copper == 25
    assert [rep.reward.name for rep in quest.rewards.reputations] == ["Argent Dawn", "Bloodsail Buccaneers"]
    assert quest.rewards.reputations[1].value == -500


def test_area_index_lists_every_quest_area(client: Client) -> None:
    index = client.quest_areas.index()

    assert index.areas[0].id == 1
    assert index.areas[0].name == "Dun Morogh"


def test_area_get_reads_quests_in_the_area(client: Client) -> None:
    area = client.quest_areas.get(1)

    assert area.area == "Dun Morogh"
    assert area.quests[0].name == "Frostmane Hold"


def test_category_index_lists_every_quest_category(client: Client) -> None:
    index = client.quest_categories.index()

    assert len(index.categories) == 33
    assert index.categories[0].name == "Epic"


def test_category_get_reads_quests_in_the_category(client: Client) -> None:
    category = client.quest_categories.get(1)

    assert category.category == "Epic"
    assert [quest.name for quest in category.quests] == [
        "Shrouded in Nightmare",
        "Waking Legends",
        "Shrouded in Nightmare",
        "Waking Legends",
    ]


def test_type_index_lists_every_quest_type(client: Client) -> None:
    index = client.quest_types.index()

    assert len(index.types) == 5
    assert index.types[0].name == "Elite"


def test_type_get_reads_quests_of_that_type(client: Client) -> None:
    quest_type = client.quest_types.get(1)

    assert quest_type.type == "Elite"
    assert len(quest_type.quests) == 465
    assert quest_type.quests[0].name == "Tharil'zun"
