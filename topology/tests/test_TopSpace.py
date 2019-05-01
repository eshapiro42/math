import pytest

from ..topology import TopSpace


def test_create_empty_topology():
    X = TopSpace(set(), [set()])
    assert isinstance(X, TopSpace)
    assert X.space == frozenset()
    assert X.open_sets == {frozenset()}

def test_create_singleton_topology():
    X = TopSpace({1}, [set(), {1}])
    assert isinstance(X, TopSpace)
    assert X.space == frozenset({1})
    assert X.open_sets == frozenset({frozenset(), frozenset({1})})

def test_create_small_topology():
    space = {1, 2, 3}
    open_sets = [
        set(),
        space,
        {1}, {2}, {3},
        {1, 2}, {2, 3}, {1, 3},
    ]
    X = TopSpace(space, open_sets)
    assert isinstance(X, TopSpace)
    assert X.space == frozenset(space)
    assert X.open_sets == frozenset(map(frozenset, open_sets))

def test_create_topology_missing_empty_set():
    with pytest.raises(ValueError):
        X = TopSpace({1}, [{1}])

def test_create_topology_missing_space():
    with pytest.raises(ValueError):
        X = TopSpace({1}, [set()])

def test_create_topology_not_closed_under_unions():
    with pytest.raises(ValueError):
        X = TopSpace({1, 2, 3}, [set(), {1, 2, 3}, {1}, {2}])

def test_create_topology_not_closed_under_intersections():
    with pytest.raises(ValueError):
        X = TopSpace({1, 2, 3}, [set(), {1, 2, 3}, {1, 2}, {2, 3}])

def test_create_topology_open_sets_not_subsets_of_space():
    with pytest.raises(ValueError):
        X = TopSpace(set(), [set(), {1}])

def test_create_topology_from_subbasis():
    space = set(range(5))
    subbasis = [{i} for i in space]
    X = TopSpace.from_subbasis(space, subbasis)
    assert X.space == frozenset(space)
    assert all([subset in X.open_sets for subset in subbasis])

def test_create_topology_from_invalid_subbasis():
    space = set(range(5))
    subbasis = []
    with pytest.raises(Exception):
        X = TopSpace.from_subbasis(space, subbasis)
    subbasis = [{0}]
    with pytest.raises(Exception):
        X = TopSpace.from_subbasis(space, subbasis)
    subbasis = [{100}]
    with pytest.raises(Exception):
        X = TopSpace.from_subbasis(space, subbasis)

def test_create_topology_from_basis():
    # TODO
    pass

def test_create_topology_from_invalid_basis():
    # TODO
    pass