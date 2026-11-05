from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_creature_families_index_lists_every_family(client: Client) -> None:
    index = client.creature_families.index()

    assert len(index.creature_families) == 27
    assert index.creature_families[0].name == "Bat"


def test_creature_families_get_reads_family_details(client: Client) -> None:
    family = client.creature_families.get(24)

    assert family.name == "Bat"
    assert family.media.id == 24


def test_creature_types_index_lists_every_type(client: Client) -> None:
    index = client.creature_types.index()

    assert len(index.creature_types) == 13
    assert index.creature_types[0].name == "Beast"


def test_creature_types_get_reads_type_details(client: Client) -> None:
    creature_type = client.creature_types.get(1)

    assert creature_type.name == "Beast"
