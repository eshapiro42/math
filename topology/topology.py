'''Classes for topological spaces and functions between them'''

import copy
import itertools

from typing import (
    AbstractSet,
    Dict,
    Iterable,
    Tuple,
    Union,
)

from common import (
    Function,
    Set,
)


class TopSpace:
    '''Topological space

    Attributes:
        open_sets (Set[Set]): the open sets in the topology
        space (Set): the underlying space
    '''

    def __init__(self, space: Set, open_sets: Set) -> None:
        # Check that all open sets are of type set or frozenset
        if not all([isinstance(x, Set) for x in open_sets]):
            raise TypeError('all open sets must be of type Set')
        # Check that the empty set is open
        if not Set() in open_sets:
            raise ValueError('the empty set must be open')
        # Check that the space itself is open
        if not space in open_sets:
            raise ValueError('the space itself must be open')
        # Check that every open set is a subset of the space
        if not all([open_set <= space for open_set in open_sets]):
            raise ValueError('all open sets must be subsets of the space')
        # Check pairwise unions
        if not self.pairwise_unions(open_sets):
            raise ValueError('open sets must be closed under unions')
        # Check pairwise intersections
        if not self.pairwise_intersections(open_sets):
            raise ValueError('open sets must be closed under intersections')
        # Cast all open sets to frozensets so they are hashable
        self.open_sets = open_sets
        self.space = space

    def __contains__(self, element):
        '''Check whether an element is in the topological space'''
        return element in self.space

    def __iter__(self):
        return iter(self.space)

    def __mul__(self, other):
        '''Given two topological spaces, return their product space'''
        # Create the product space from the cartestian product of self.space and other.space
        product_space = itertools.product(self.space, other.space)
        # Create a basis for the product topology from the cartesian products of open sets
        product_basis = [itertools.product(set1, set2)
                         for set1 in self.open_sets
                         for set2 in other.open_sets]
        # Create a topology from the basis
        product = TopSpace.from_basis(product_space, list(map(set, product_basis)))
        return product

    def __eq__(self, other) -> bool:
        '''Check whether two topological spaces are equal'''
        # Topological spaces are equal if their underlying spaces are equal
        # and they have the same open sets
        return self.space == other.space and self.open_sets == other.open_sets

    def __le__(self, other) -> bool:
        '''Check whether a space is a subset of another'''
        try:
            return self.space <= other.space
        except:
            return self.space <= other

    def __lt__(self, other) -> bool:
        '''Check whether a space is a proper subset of another'''
        try:
            return self.space < other.space
        except:
            return self.space < other

    def __ge__(self, other) -> bool:
        '''Check whether a set or space is a superset of another'''
        try:
            return other.space <= self.space
        except:
            return other <= self.space

    def __gt__(self, other) -> bool:
        '''Check whether a set or space is a proper superset of another'''
        try:
            return other.space < self.space
        except:
            return other < self.space

    def is_closed(self, subset: AbstractSet) -> bool:
        '''Check whether a subset of a topological space is closed'''
        # A set is closed if its complement is open
        return self.space - subset in self.open_sets

    @staticmethod
    def pairwise_unions(subsets: Set) -> bool:
        '''Check whether a collection of subsets is closed under pairwise unions'''
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Make sure their union is in subsets
            if not set1 | set2 in subsets:
                return False
        return True

    @staticmethod
    def pairwise_intersections(subsets: Set) -> bool:
        '''Check whether a collection of subsets is closed under pairwise intersections'''
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Make sure their intersection is in subsets
            if not set1 & set2 in subsets:
                return False
        return True

    @staticmethod
    def is_basis(space: Set, subsets: Set):
        '''Check whether a collection of subsets is a basis for a topology on a set'''
        # Check that every point in the space is in some subset
        if not all([any([point in subset for subset in subsets]) for point in space]):
            return False
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Compute their intersection
            intersection = set1 & set2
            # If the intersection is empty, we're fine
            if not intersection:
                continue
            # Otherwise, we need to make sure every point in the intersection is
            # contained in some basis subset which is contained in the intersection
            if not any([point in subset and subset <= intersection
                        for subset in subsets
                        for point in intersection]):
                return False
        return True

    @staticmethod
    def is_subbasis(space: Set, subsets: Set):
        '''Check whether a collection of subsets is a subbasis for a topology on a set'''
        # Check that every point in the space is in some subset
        if not all([any([point in subset for subset in subsets]) for point in space]):
            return False
        return True

    @classmethod
    def from_subbasis(cls, space: Set, subbasis: Set):
        '''Construct a topological space from a subbasis

        This method has exponential runtime complexity and is slow for large subbases.
        '''
        # Check that all subsets are of type Set
        if not all([isinstance(x, Set) for x in subbasis]):
            raise TypeError('all subbasis elements must be sets')
        # Check that subbasis is actually a subbasis
        if not cls.is_subbasis(space, subbasis):
            raise ValueError('a subbasis must cover all points in the space')
        # Add the empty set
        subbasis.add(Set())
        basis = copy.deepcopy(subbasis)
        # For each number idx up to len(subbasis), append the
        # intersections of all idx-length combinations
        for idx, _ in enumerate(subbasis, start=1):
            combinations = itertools.combinations(subbasis, idx)
            for combination in combinations:
                intersection = copy.deepcopy(space)
                for subset in combination:
                    intersection &= subset
                basis.add(intersection)
        # basis is now a basis
        top = cls.from_basis(space, basis)
        return top

    @classmethod
    def from_basis(cls, space: Set, basis: Set):
        '''Construct a topological space from a basis

        This method has exponential runtime complexity and is slow for large bases.
        '''
        # Check that all subsets are of type Set
        if not all([isinstance(x, Set) for x in basis]):
            raise TypeError('all basis elements must be sets')
        # Check that basis is actually a basis
        if not cls.is_basis(space, basis):
            raise ValueError('not a valid basis for a topology')
        # Add the empty set
        basis.add(Set())
        open_sets = copy.deepcopy(basis)
        # For each number idx up to len(basis), append the
        # unions of all idx-length combinations
        for idx, _ in enumerate(basis, start=1):
            combinations = itertools.combinations(basis, idx)
            for combination in combinations:
                union = set()
                for subset in combination:
                    union |= subset
                open_sets.add(union)
        # Create a topology from open_sets
        top = cls(space, open_sets)
        return top

class TopFunction(Function):
    '''TopFunction (mapping between TopSpaces)

    Attributes:
        mapping (dict): value, image pairs (basically {x: f(x) for x in domain})
        domain (TopSpace): the function's domain
        codomain (TopSpace): the function's codomain

    Properties:
        inverse (TopFunction): the function's inverse, if it has one
        is_continuous (bool): whether the function is continuous
        is_homeomorphism (bool): whether the function is a homeomorphism
    '''

    def __init__(self, mapping: dict, domain: TopSpace, codomain: TopSpace):
        if not isinstance(domain, TopSpace) or not isinstance(codomain, TopSpace):
            raise TypeError('domain and codomain must be of type TopSpace')
        super().__init__(mapping, domain, codomain)

    def __matmul__(self, other):
        '''Create a new function from the composition self . other'''
        mapping = {k: self.mapping[other.mapping[k]] for k in other.mapping}
        return TopFunction(mapping, other.domain, self.codomain)    

    @property
    def inverse(self):
        '''Create a new function which is the inverse of this one'''
        if not self.is_bijective:
            raise ValueError('this function is not invertible')
        mapping = {v: k for k, v in self.mapping.items()}
        return TopFunction(mapping, self.codomain, self.domain)

    @property
    def is_continuous(self):
        '''Check whether a function between topological spaces is continuous'''
        # Check that the preimage of any open set is open
        return all([self.preimage(open_set) in self.domain.open_sets
                    for open_set in self.codomain.open_sets])

    @property
    def is_homeomorphism(self):
        '''Check whether a function between topological spaces is a homeomorphism'''
        # Check that the function is bijective
        if not self.is_bijective:
            return False
        # Check that the function is continuous
        if not self.is_continuous:
            return False
        # Check that the function's inverse is continuous
        if not self.inverse.is_continuous:
            return False
        return True