from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_specialization(client: Client) -> None:
    index = client.playable_specializations.index()

    assert len(index.character_specializations) == 27
    assert index.character_specializations[0].name == "Elemental Combat"


def test_get_reads_specialization_details(client: Client) -> None:
    spec = client.playable_specializations.get(375)

    assert spec.name == "Elemental Combat"
    assert spec.playable_class.name == "Shaman"
    assert spec.power_type.name == "Mana"
    assert spec.spec_talent_tree.name == "Elemental Combat"
    assert spec.media.id == 375
