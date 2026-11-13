from functools import cached_property

import pytest

import wow.resources
from wow import AsyncClient, Client


@pytest.mark.parametrize("client_class", [Client, AsyncClient])
def test_every_resource_namespace_is_exported_for_annotations(client_class: type[Client | AsyncClient]) -> None:
    namespaces = {
        name: attribute.func.__annotations__["return"]
        for name, attribute in vars(client_class).items()
        if isinstance(attribute, cached_property)
    }

    assert len(namespaces) == 37
    for name, resource_class in namespaces.items():
        assert getattr(wow.resources, resource_class.__name__) is resource_class, name
