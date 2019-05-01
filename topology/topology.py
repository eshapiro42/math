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


class TopSpace:
    '''Topological space

    Attributes:
        open_sets (frozenset[frozenset]): the open sets in the topology
        space (frozenset): the underlying space
    '''

    def __init__(self, space: Union[set, frozenset], open_sets: Iterable[AbstractSet]) -> None:
        # Check that all open sets are of type set or frozenset
        if not all([isinstance(x, (set, frozenset)) for x in open_sets]):
            raise TypeError('all open sets must be of type set or frozenset')
        # Check that the empty set is open
        if not set() in open_sets:
            raise ValueError('the empty set must be open')
        # Check that the space itself is open
        if not space in open_sets:
            raise ValueError('the space itself must be open')
        # Check that every open set is a subset of the space
        if not all([open_set <= space for open_set in open_sets]):
            raise ValueError('all open sets must be subsets of the space')
        # Check pairwise unions
        unions, set1, set2 = self.pairwise_unions(open_sets)
        if not unions:
            raise ValueError('{} and {} are open but their union {} is not'.format(
                set1,
                set2,
                set1 | set2))
        # Check pairwise intersections
        intersections, set1, set2 = self.pairwise_intersections(open_sets)
        if not intersections:
            raise ValueError('{} and {} are open but their intersection {} is not'.format(
                set1,
                set2,
                set1 & set2))
        # Cast all open sets to frozensets so they are hashable
        self.open_sets = frozenset(map(frozenset, open_sets))
        self.space = frozenset(space)

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

    def is_closed(self, subset: AbstractSet) -> bool:
        '''Check whether a subset of a topological space is closed'''
        # A set is closed if its complement is open
        return self.space - subset in self.open_sets

    @staticmethod
    def pairwise_unions(subsets: Iterable[AbstractSet]) -> Tuple[bool, AbstractSet, AbstractSet]:
        '''Check whether a collection of subsets is closed under pairwise unions'''
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Make sure their union is in subsets
            if not set1 | set2 in subsets:
                return False, set1, set2
        return True, None, None

    @staticmethod
    def pairwise_intersections(
            subsets: Iterable[AbstractSet]) -> Tuple[bool, AbstractSet, AbstractSet]:
        '''Check whether a collection of subsets is closed under pairwise intersections'''
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Make sure their intersection is in subsets
            if not set1 & set2 in subsets:
                return False, set1, set2
        return True, None, None

    @staticmethod
    def is_basis(space: AbstractSet, subsets: Iterable[AbstractSet]):
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
    def is_subbasis(space: AbstractSet, subsets: Iterable[AbstractSet]):
        '''Check whether a collection of subsets is a subbasis for a topology on a set'''
        # Check that every point in the space is in some subset
        if not all([any([point in subset for subset in subsets]) for point in space]):
            return False
        return True

    @classmethod
    def from_subbasis(cls, space: AbstractSet, subbase_subsets: Iterable[AbstractSet]):
        '''Construct a topological space from a subbasis

        This method has exponential runtime complexity and is slow for large subbases.
        '''
        # Check that all subsets are of type set or frozenset
        if not all([isinstance(x, (set, frozenset)) for x in subbase_subsets]):
            raise TypeError('all elements of the topology must be sets')
        # Check that subbase_subsets is actually a subbasis
        if not cls.is_subbasis(space, subbase_subsets):
            raise ValueError('a subbasis must cover all points in the space')
        # Add the empty set
        subbase_subsets.append(set())
        subbase_subsets = list(map(frozenset, subbase_subsets))
        base_subsets = copy.deepcopy(subbase_subsets)
        # For each number idx up to len(subbasis), append the
        # intersection of all idx-length combinations
        for idx, _ in enumerate(subbase_subsets, start=1):
            combinations = itertools.combinations(subbase_subsets, idx)
            for combination in combinations:
                intersection = copy.deepcopy(space)
                for subset in combination:
                    intersection &= subset
                base_subsets.append(intersection)
        basis = list(set(map(frozenset, base_subsets)))
        # base_subsets is now a basis
        top = cls.from_basis(space, basis)
        return top

    @classmethod
    def from_basis(cls, space: AbstractSet, base_subsets: Iterable[AbstractSet]):
        '''Construct a topological space from a basis

        This method has exponential runtime complexity and is slow for large bases.
        '''
        # Check that all subsets are of type set or frozenset
        if not all([isinstance(x, (set, frozenset)) for x in base_subsets]):
            raise TypeError('all elements of the topology must be sets')
        # Check that base_subsets is actually a basis
        if not cls.is_basis(space, base_subsets):
            raise ValueError('not a valid basis for a topology')
        # Add the empty set
        base_subsets.append(set())
        base_subsets = list(map(frozenset, base_subsets))
        subsets = copy.deepcopy(base_subsets)
        # For each number idx up to len(subbasis), append the
        # union of all idx-length combinations
        for idx, _ in enumerate(base_subsets, start=1):
            combinations = itertools.combinations(base_subsets, idx)
            for combination in combinations:
                union = set()
                for subset in combination:
                    union |= subset
                subsets.append(union)
        open_sets = list(set(map(frozenset, subsets)))
        # Create a topology from open_sets
        top = cls(space, open_sets)
        return top

class Function:
    '''Function (mapping between sets)

    Attributes:
        mapping (dict): value, image pairs (basically {x: f(x) for x in domain})
        domain (frozenset): the function's domain
        codomain (frozenset): the function's codomain
    '''

    def __init__(self, mapping: Dict, domain: AbstractSet, codomain: AbstractSet) -> None:
        # Check that all elements of the domain get mapped
        if not all([point in mapping.keys() for point in domain.space]):
            raise ValueError('all values in the domain must get mapped')
        # Check that everything in the mapping is valid
        for key, val in mapping.items():
            if key not in domain.space:
                raise ValueError('value {} is not in the domain'.format(key))
            if val not in codomain.space:
                raise ValueError('value {} is not in the codomain'.format(val))
        self.mapping = mapping
        self.domain = domain
        self.codomain = codomain

    def __call__(self, value):
        '''Given a value, return its image under the function'''
        try:
            return self.mapping[value]
        except:
            raise ValueError('{} is not in the domain'.format(value))

    def __matmul__(self, other):
        '''Create a new function from the composition self . other'''
        mapping = {k: self.mapping[other.mapping[k]] for k in other.mapping}
        return Function(mapping, other.domain, self.codomain)

    def __eq__(self, other):
        '''Check if two functions are equal'''
        return (self.domain == other.domain
                and self.codomain == other.codomain
                and self.mapping == other.mapping)

    def inverse(self):
        '''Create a new function which is the inverse of this one'''
        if not self.is_bijective():
            raise ValueError('this function is not invertible')
        mapping = {v: k for k, v in self.mapping.items()}
        return Function(mapping, self.codomain, self.domain)

    def fiber(self, value):
        '''Get the preimage of a single value in the codomain'''
        if value not in self.codomain:
            raise ValueError('{} is not in the codomain'.format(value))
        fiber = frozenset(k for k in self.mapping if self.mapping[k] == value)
        return fiber

    def preimage(self, subset: AbstractSet):
        '''Get the preimage of a subset of the codomain'''
        if not subset <= self.codomain:
            raise ValueError('{} if not a subset of the codomain'.format(subset))
        preimage = set()
        for value in subset:
            preimage |= self.fiber(value)
        return preimage

    def image(self, subset: AbstractSet):
        '''Take the image of a subset under the funciton'''
        img = set()
        for value in subset:
            img |= self(value)
        return img

    def is_bijective(self):
        '''Check whether the function is a bijection'''
        # Check for surjectivity
        if not all([v in self.mapping.values() for v in self.codomain.space]):
            return False
        # Check for injectivity
        if not all([len(self.fiber(v)) == 1 for v in self.mapping.values()]):
            return False
        return True

    def is_continuous(self):
        '''Check whether a function between topological spaces is continuous'''
        # Check that the preimage of any open set is open
        return all([self.preimage(openset) in self.domain.subsets
                    for openset in self.codomain.subsets])

    def is_homeomorphism(self):
        '''Check whether a function between topological spaces is a homeomorphism'''
        # Check that the function is bijective
        if not self.is_bijective():
            return False
        # Check that the function is continuous
        if not self.is_continuous():
            return False
        # Check that the function's inverse is continuous
        if not self.inverse().is_continuous():
            return False
        return True
