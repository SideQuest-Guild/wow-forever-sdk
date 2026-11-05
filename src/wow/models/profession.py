"""Models for the Profession API."""

from wow.models._common import Document, IdRef, Model, Ref, TypedName

__all__ = ["Profession", "ProfessionIndex", "ProfessionSkillTier", "RecipeCategory"]


class ProfessionIndex(Document):
    """Every profession, primary and secondary."""

    professions: tuple[Ref, ...]


class Profession(Document):
    """A profession, such as Tailoring, with its skill tiers."""

    id: int
    name: str
    description: str
    type: TypedName
    media: IdRef
    skill_tiers: tuple[Ref, ...] = ()


class RecipeCategory(Model):
    """A group of recipes in a skill tier, such as Weapon Stones."""

    name: str
    recipes: tuple[Ref, ...] = ()


class ProfessionSkillTier(Document):
    """One skill tier of a profession: its skill range and every recipe in it, by category."""

    id: int
    name: str
    minimum_skill_level: int
    maximum_skill_level: int
    categories: tuple[RecipeCategory, ...] = ()
