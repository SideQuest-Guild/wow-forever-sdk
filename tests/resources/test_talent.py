from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_talent_index_lists_every_talent(client: Client) -> None:
    index = client.talents.index()

    assert index.talents[0].id == 134370
    assert index.talents[0].name == "Improved Tranquility"


def test_talent_get_reads_talent_details(client: Client) -> None:
    talent = client.talents.get(134370)

    assert talent.playable_class.name == "Druid"
    assert talent.playable_specialization.name == "Restoration"
    assert talent.spell.name == "Improved Tranquility"
    assert talent.spell.id == 17123
    assert [rank.rank for rank in talent.rank_descriptions] == [1, 2]
    assert "50%" in talent.rank_descriptions[0].description


def test_talent_tree_index_lists_class_and_spec_trees(client: Client) -> None:
    index = client.talent_trees.index()

    assert len(index.class_talent_trees) == 9
    assert index.class_talent_trees[0].name == "Druid"
    assert len(index.spec_talent_trees) == 27
    assert index.spec_talent_trees[0].name == "Balance"


def test_talent_tree_get_reads_the_spec_talent_tree(client: Client) -> None:
    tree = client.talent_trees.get(1089, 574)

    assert tree.id == 1089
    assert tree.name == "Balance"
    assert tree.playable_class.name == "Druid"
    assert tree.playable_specialization.name == "Balance"
    assert len(tree.spec_talent_nodes) == 16
    first_node = tree.spec_talent_nodes[0]
    assert first_node.id == 104923
    assert first_node.node_type.type == "ACTIVE"
    assert first_node.ranks[0].tooltip.talent.name == "Improved Wrath"
    assert first_node.ranks[0].tooltip.spell_tooltip.spell.name == "Improved Wrath"
    node_with_lock = next(node for node in tree.spec_talent_nodes if node.id == 104928)
    assert node_with_lock.locked_by == (104927,)
