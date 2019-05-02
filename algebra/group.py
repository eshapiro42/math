'''Classes for groups and functions between them'''

import copy
import itertools

from common import (
    Function,
    Set,
)


class GroupElement:
    '''GroupElement'''

    def __init__(self, value, group):
        self.value = value
        self.group = group

    def __repr__(self):
        return 'GroupElement({}, {})'.format(self.value, self.group)

    def __str__(self):
        return self.value

    def __mul__(self, other):
        # Elements must come from the same group
        if not self.group == other.group:
            raise ValueError('elements are from different groups')
        product = self.group.products[(self.value, other.value)]
        return GroupElement(product, self.group)

    def __invert__(self):
        '''Find this element's inverse'''
        for candidate in self.group.group_set:
            if self.group.products[(self.value, candidate)] == self.group.identity.value:
                return GroupElement(candidate, self.group)


class Group:
    '''Group

    Attributes:
        products (dict): a mapping of pairs of elements to their product
        group_set (Set): the underlying set
    '''

    def __init__(self, group_set: Set, products: dict) -> None:
        if not self.closed_under_products(group_set, products):
            raise ValueError('not closed under products')
        identity = self.get_identity(group_set, products)
        if identity is None:
            raise ValueError('there is no identity element')
        if not self.closed_under_inverses(group_set, products, identity):
            raise ValueError('not closed under inverses')
        if not self.is_associative(group_set, products):
            raise ValueError('not associative')
        self.identity = GroupElement(identity, self)
        self.group_set = group_set
        self.products = products

    @staticmethod
    def closed_under_products(group_set: Set, products: dict) -> bool:
        '''Check for closure under products'''
        # Check that nothing is included that is not in group_set
        for key, value in products.items():
            if not all([element in group_set for element in [key[0], key[1], value]]):
                return False
        # Check that everything in group_set is accounted for
        for pair in itertools.product(group_set, repeat=2):
            if pair not in products:
                return False
        return True

    @staticmethod
    def get_identity(group_set: Set, products: dict) -> bool:
        '''Check for an identity element'''
        # loop through each element to see if it is the identity
        for candidate in group_set:
            # Check its product with all elements to see if it's always absorbed
            if all([products[(candidate, other)] == other and products[(other, candidate)] == other
                    for other in group_set]):
                return candidate
        return None

    @staticmethod
    def closed_under_inverses(group_set: Set, products: dict, identity) -> bool:
        # Loop through each element
        for element in group_set:
            # Check that it has an inverse
            if not any([products[(element, other)] == identity] for other in group_set):
                return False
        return True

    @staticmethod
    def is_associative(group_set: Set, products: dict) -> bool:
        '''Check that the group operation is associative'''
        for first, second, third in itertools.product(group_set, repeat=3):
            if products[(products[(first, second)], third)] != products[(first, products[(second, third)])]:
                return False
        return True

    def __call__(self, element):
        '''Returns a GroupElement from element'''
        return GroupElement(element, self)

    def __contains__(self, element):
        '''Check whether an element is in the group'''
        return element in self.group_set

    def __iter__(self):
        return iter(self.group_set)

    def __mul__(self, other):
        '''Given two groups, return their direct product'''
        pass

    def __eq__(self, other) -> bool:
        '''Check whether two groups are equal'''
        # Groups are equal if their underlying sets are equal
        # and they have the same products
        return self.group_set == other.group_set and self.products == other.products

    def __le__(self, other) -> bool:
        '''Check whether a group is a subset of another'''
        try:
            return self.group_set <= other.group_set
        except:
            return self.group_set <= other

    def __lt__(self, other) -> bool:
        '''Check whether a group is a proper subset of another'''
        try:
            return self.group_set < other.group_set
        except:
            return self.group_set < other

    def __ge__(self, other) -> bool:
        '''Check whether a set or group is a superset of another'''
        try:
            return other.group_set <= self.group_set
        except:
            return other <= self.group_set

    def __gt__(self, other) -> bool:
        '''Check whether a set or group is a proper superset of another'''
        try:
            return other.group_set < self.group_set
        except:
            return other < self.group_set


class GroupFunction(Function):
    '''GroupFunction (mapping between Groups)

    Attributes:
        mapping (dict): value, image pairs (basically {x: f(x) for x in domain})
        domain (Group): the function's domain
        codomain (Group): the function's codomain

    Properties:
        inverse (GorupFunction): the function's inverse, if it has one
        is_homomorphism (bool): whether the function is a homomorphism
        is_isomorphism (bool): whether the function is an isomorphism
    '''

    def __init__(self, mapping: dict, domain: Group, codomain: Group):
        if not isinstance(domain, Group) or not isinstance(codomain, Group):
            raise TypeError('domain and codomain must be of type Group')
        super().__init__(mapping, domain, codomain)

    def __matmul__(self, other):
        '''Create a new function from the composition self . other'''
        mapping = {k: self.mapping[other.mapping[k]] for k in other.mapping}
        return GroupFunction(mapping, other.domain, self.codomain)    

    @property
    def inverse(self):
        '''Create a new function which is the inverse of this one'''
        if not self.is_bijective:
            raise ValueError('this function is not invertible')
        mapping = {v: k for k, v in self.mapping.items()}
        return GroupFunction(mapping, self.codomain, self.domain)

    @property
    def is_homeomorphism(self):
        '''Check whether a function between topological spaces is a homomorphism'''
        pass