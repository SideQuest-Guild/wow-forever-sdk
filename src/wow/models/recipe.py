"""Models for the Recipe API."""

from wow.models._common import Document, IdRef, Model, Ref
from wow.models.item import ItemReagent

__all__ = ["CraftedQuantity", "Recipe"]


class CraftedQuantity(Model):
    """How many items one craft makes: a fixed ``value``, or a range from ``minimum`` to ``maximum``."""

    value: float | None = None
    minimum: float | None = None
    maximum: float | None = None


class Recipe(Document):
    """A profession recipe: what it makes and the reagents it uses.

    Attributes:
        crafted_item: The item the recipe makes. Recipes that make no item, such as enchants, have none.
        crafted_quantity: How many items one craft makes. Recipes that craft nothing, such as the one that teaches
            Skinning, have none.
        rank: The rank of a recipe that has several ranks.
    """

    id: int
    name: str
    media: IdRef
    crafted_quantity: CraftedQuantity | None = None
    reagents: tuple[ItemReagent, ...] = ()
    crafted_item: Ref | None = None
    rank: int | None = None
    description: str | None = None
