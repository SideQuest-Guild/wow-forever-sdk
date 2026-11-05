from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_power_type(client: Client) -> None:
    index = client.power_types.index()

    assert len(index.power_types) == 6
    assert [power.name for power in index.power_types] == [
        "Mana",
        "Rage",
        "Focus",
        "Energy",
        "Combo Points",
        "Happiness",
    ]


def test_get_reads_power_type_details(client: Client) -> None:
    mana = client.power_types.get(0)

    assert mana.id == 0
    assert mana.name == "Mana"
