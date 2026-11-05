from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_pet(client: Client) -> None:
    index = client.pets.index()

    assert len(index.pets) == 109
    assert index.pets[0].name == "Brown Ground Squirrel"


def test_get_reads_pet_details(client: Client) -> None:
    pet = client.pets.get(5154)

    assert pet.name == "Brown Ground Squirrel"
    assert pet.battle_pet_type.name == "Critter"
    assert pet.battle_pet_type.type == "CRITTER"
    assert pet.creature.name == "Brown Ground Squirrel"
    assert pet.is_tradable is True
    assert pet.is_capturable is False
    assert pet.media.id == 5154
