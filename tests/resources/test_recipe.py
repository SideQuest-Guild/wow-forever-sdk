from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_get_reads_what_a_recipe_makes_and_uses(client: Client) -> None:
    boots = client.recipes.get(1353)

    assert boots.name == "Handstitched Leather Boots"
    assert boots.crafted_item is not None
    assert boots.crafted_item.name == "Handstitched Leather Boots"
    assert boots.crafted_quantity is not None
    assert boots.crafted_quantity.value == 1
    assert [(reagent.reagent.name, reagent.quantity) for reagent in boots.reagents] == [
        ("Light Leather", 2),
        ("Coarse Thread", 1),
    ]


def test_an_enchant_makes_no_item(client: Client) -> None:
    enchant = client.recipes.get(4289)

    assert enchant.crafted_item is None
    assert enchant.description is not None
    assert enchant.description.startswith("Permanently enchant bracers")


def test_a_recipe_that_teaches_a_profession_crafts_nothing(client: Client) -> None:
    skinning = client.recipes.get(4766)

    assert skinning.name == "Skinning"
    assert (skinning.crafted_quantity, skinning.crafted_item) == (None, None)


def test_some_recipes_make_a_range_of_items(client: Client) -> None:
    quantity = client.recipes.get(2427).crafted_quantity

    assert quantity is not None
    assert (quantity.value, quantity.minimum, quantity.maximum) == (None, 1, 4)


def test_ranked_recipes_carry_their_rank(client: Client) -> None:
    assert client.recipes.get(52639).rank == 1


def test_media_reads_the_icon(client: Client) -> None:
    icon = client.recipes.media(1631).assets[0]

    assert icon.value == "https://render.worldofwarcraft.com/forever-us/icons/56/135248.jpg"
