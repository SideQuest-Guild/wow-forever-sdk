from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_achievements_index_lists_every_achievement(client: Client) -> None:
    index = client.achievements.index()

    assert len(index.achievements) == 176
    assert index.achievements[0].name == "Rank 3"


def test_achievements_get_reads_achievement_details(client: Client) -> None:
    achievement = client.achievements.get(62041)

    assert achievement.name == "Rank 3"
    assert achievement.description == "Reach the rank of Sergeant in the Player vs. Player Honor System."
    assert achievement.points == 0
    assert achievement.is_account_wide is True
    assert achievement.category.name == "Ranks"
    assert achievement.criteria.id == 230739
    assert achievement.criteria.description == "Rank 3"
    assert achievement.media.id == 62041
    assert achievement.reward_description == "Earn 1 Legacy Point."


def test_achievements_media_reads_the_icon(client: Client) -> None:
    media = client.achievements.media(62041)

    assert media.assets[0].key == "icon"
    assert "/forever-us/icons/" in media.assets[0].value


def test_achievement_categories_index_lists_categories_and_roots(client: Client) -> None:
    index = client.achievement_categories.index()

    assert len(index.categories) == 29
    assert index.categories[0].name == "Classes"
    assert len(index.root_categories) == 7
    assert index.root_categories[0].name == "Classes"


def test_achievement_categories_get_reads_category_details(client: Client) -> None:
    category = client.achievement_categories.get(15568)

    assert category.name == "Classes"
    assert category.is_guild_category is False
    assert category.display_order == 3
    assert [sub.name for sub in category.subcategories[:3]] == ["Druid", "Hunter", "Mage"]
    assert category.aggregates_by_faction is not None
    assert category.aggregates_by_faction["alliance"].quantity == 54
    assert category.aggregates_by_faction["horde"].points == 0
