from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_profession(client: Client) -> None:
    index = client.professions.index()

    assert len(index.professions) == 13
    assert index.professions[0].name == "Tailoring"


def test_get_reads_profession_details(client: Client) -> None:
    tailoring = client.professions.get(197)

    assert tailoring.name == "Tailoring"
    assert tailoring.type.type == "PRIMARY"
    assert tailoring.type.name == "Primary"
    assert tailoring.media.id == 197
    assert len(tailoring.skill_tiers) == 1
    assert tailoring.skill_tiers[0].name == "Tailoring"


def test_skill_tier_lists_recipes_by_category(client: Client) -> None:
    tier = client.professions.skill_tier(164, 2938)

    assert tier.name == "Blacksmithing"
    assert (tier.minimum_skill_level, tier.maximum_skill_level) == (1, 75)
    assert tier.categories[0].name == "Weapon Stones"
    assert tier.categories[0].recipes[0].name == "Rough Sharpening Stone"


def test_media_reads_the_icon(client: Client) -> None:
    assert client.professions.media(164).assets[0].file_data_id == 136241
