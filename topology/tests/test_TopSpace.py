import pytest

from ..topology import TopSpace, Set


def test_create_empty_topology():
    space = Set()
    open_sets = Set(space)
    X = TopSpace(space, open_sets)
    assert isinstance(X, TopSpace)
    assert X.space == space
    assert X.open_sets == open_sets

def test_create_singleton_topology():
    space = Set(1)
    open_sets = Set(Set(), space)
    X = TopSpace(space, open_sets)
    assert isinstance(X, TopSpace)
    assert X.space == space
    assert X.open_sets == open_sets

def test_create_small_topology():
    space = Set(1, 2, 3)
    open_sets = Set(
        Set(),
        space,
        Set(1), Set(2), Set(3),
        Set(1, 2), Set(2, 3), Set(1, 3)
    )
    X = TopSpace(space, open_sets)
    assert isinstance(X, TopSpace)
    assert X.space == space
    assert X.open_sets == open_sets

def test_create_discrete_topology():
    space = Set(*range(5))
    open_sets = space.powerset
    X = TopSpace(space, open_sets)
    assert isinstance(X, TopSpace)
    assert X.space == space
    assert X.open_sets == open_sets

def test_create_topology_missing_empty_set():
    space = Set(1)
    open_sets = Set(space)
    with pytest.raises(ValueError):
        TopSpace(space, open_sets)

def test_create_topology_missing_space():
    space = Set(1)
    open_sets = Set(Set())
    with pytest.raises(ValueError):
        TopSpace(space, open_sets)

def test_create_topology_not_closed_under_unions():
    space = Set(1, 2, 3)
    open_sets = Set(
        Set(),
        space,
        Set(1), Set(2)
    )
    with pytest.raises(ValueError):
        TopSpace(space, open_sets)

def test_create_topology_not_closed_under_intersections():
    space = Set(1, 2, 3)
    open_sets = Set(
        Set(),
        space,
        Set(1, 2), Set(2, 3)
    )
    with pytest.raises(ValueError):
        TopSpace(space, open_sets)

def test_create_topology_open_sets_not_subsets_of_space():
    space = Set()
    open_sets = Set(
        space,
        Set(1)
    )
    with pytest.raises(ValueError):
        TopSpace(space, open_sets)

def test_create_topology_from_subbasis():
    space = Set(*range(5))
    subbasis = Set(*[Set(i) for i in space])
    X = TopSpace.from_subbasis(space, subbasis)
    assert X.space == space
    assert all([subset in X.open_sets for subset in subbasis])

def test_create_topology_from_invalid_subbasis():
    space = Set(*range(5))
    subbasis = Set()
    with pytest.raises(Exception):
        TopSpace.from_subbasis(space, subbasis)
    subbasis = Set(Set(0))
    with pytest.raises(Exception):
        TopSpace.from_subbasis(space, subbasis)
    subbasis = Set(Set(100))
    with pytest.raises(Exception):
        TopSpace.from_subbasis(space, subbasis)

def test_create_topology_from_basis():
    # TODO
    pass

def test_create_topology_from_invalid_basis():
    # TODO
    pass