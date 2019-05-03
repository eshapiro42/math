'''Classes for groups and functions between them'''

import collections
import itertools

from common import (
    Function,
    Set,
)


# class GroupElement(collections.Hashable):
#     '''GroupElement'''

#     def __init__(self, value, group):
#         if value not in group:
#             raise ValueError('value is not in group')
#         self.value = value
#         self.group = group

#     def __hash__(self):
#         return super().__hash__()

#     def __eq__(self, other):
#         '''Test whether two GroupElements are equal.

#         This checks only the element's value and does not demand they come from
#         the same group. This is purposely done so that subgroup elements will
#         be treated as belonging to multiple groups.
#         '''
#         return self.value == other.value

#     def __repr__(self):
#         return '{}({})'.format(self.group.name, self.value)

#     def __str__(self):
#         return str(self.value)

#     def __mul__(self, other):
#         # Elements must come from the same group
#         if not self.group == other.group:
#             raise ValueError('elements are from different groups')
#         product = self.group.products[(self.value, other.value)]
#         return GroupElement(product, self.group)

#     def __add__(self, other):
#         if self.group.abelian:
#             return self * other
#         else:
#             raise NotImplementedError('addition is not implemented for non-abelian groups')

#     def __invert__(self):
#         '''Find this element's inverse'''
#         for candidate in self.group.group_set:
#             if self.group.products[(self.value, candidate)] == self.group.identity.value:
#                 return GroupElement(candidate, self.group)
#         raise ValueError('no inverse found')


class Group(Set):
    '''Group

    Attributes:
        products (dict): a mapping of pairs of elements to their product
        group_set (Set): the underlying set
    '''

    def __init__(self, group_set: Set, products: dict) -> None:
        super().__init__(*group_set)
        self.products = products
        if not self.closed_under_products():
            raise ValueError('not closed under products')
        self.identity = self.get_identity()
        if self.identity is None:
            raise ValueError('there is no identity element')
        if not self.closed_under_inverses():
            raise ValueError('not closed under inverses')
        if not self.is_associative():
            raise ValueError('not associative')
        self.abelian = self.is_abelian()
    
    def __repr__(self):
        return 'Group({})'.format(', '.join(map(repr, self.elements)))
        
    def closed_under_products(self) -> bool:
        '''Check for closure under products'''
        # Check that nothing is included that is not in the group
        for (factor1, factor2), product in self.products.items():
            if not all([element in self for element in [factor1, factor2, product]]):
                return False
        # Check that everything in the group is accounted for
        for pair in itertools.product(self, repeat=2):
            if pair not in self.products:
                return False
        return True

    def get_identity(self) -> bool:
        '''Check for an identity element'''
        # loop through each element to see if it is the identity
        for candidate in self:
            # Check its product with all elements to see if it's always absorbed
            if all([
                    self.products[(candidate, other)] == self.products[(other, candidate)] == other
                    for other in self
            ]):
                return candidate
        return None

    def closed_under_inverses(self) -> bool:
        '''Check for inverses for each element
        
        This method has the side effect of creating a dictionary of inverses.
        '''
        self.inverses = {}
        # Loop through each element
        for element in self:
            # If we've already found element to be the inverse of something
            if element in self.inverses.values():
                # That something is the inverse of element
                self.inverses[element] = list(self.inverses.keys())[list(self.inverses.values()).index(element)]
                continue
            # Otherwise, we need to look for its inverse
            for other in self:
                if self.products[(element, other)] == self.identity:
                    self.inverses[element] = other
                    break
            else:
                # If we got here, no inverse was found for element
                return False
        # If we got here, an inverse was found for every element
        return True

    def is_associative(self) -> bool:
        '''Check that the group operation is associative'''
        triples = itertools.product(self, repeat=3)
        for a, b, c in triples:
            if self.products[(self.products[(a, b)], c)] != self.products[(a, self.products[(b, c)])]:
                return False
        return True

    def is_abelian(self) -> bool:
        '''Check that the group is commutative'''
        pairs = itertools.combinations(self, 2)
        if not all([self.products[(a, b)] == self.products[(b, a)] for a, b in pairs]):
            return False
        return True
    
    def inverse(self, element):
        '''Get the inverse of a group element'''
        return self.inverses[element]

    def __call__(self, *elements):
        '''Compute the product of elements'''
        product = self.identity
        for element in elements:
            product = self.products[(product, element)]
        return product

    def __mul__(self, other):
        '''Given two groups, compute their direct product'''
        product_set = Set(*itertools.product(self, other))
        pairs = itertools.product(product_set, repeat=2)
        product_product = {((a, b), (c, d)): (self(a, c), other(b, d)) for (a, b), (c, d) in pairs}
        product = Group(product_set, product_product)
        return product

    def __eq__(self, other) -> bool:
        '''Check whether two groups are equal'''
        # Groups are equal if their underlying sets are equal
        # and they have the same products
        return super().__eq__(other) and self.products == other.products
    
    def __leq__(self, other) -> bool:
        '''Check whether a group is a subgroup of another'''
        # Self is a subgroup of other if it is a subset and
        # its product dictionary is a subdictionary of other's
        return super().__leq__(other) and all(item in other.products.items() for item in self.products.items())

class GroupFunction(Function):
    '''GroupFunction (mapping between Groups)

    Attributes:
        mapping (dict): value, image pairs (basically {x: f(x) for x in domain})
        domain (Group): the function's domain
        codomain (Group): the function's codomain

    Properties:
        inverse (GroupFunction): the function's inverse, if it has one
        is_homomorphism (bool): whether the function is a homomorphism
        is_isomorphism (bool): whether the function is an isomorphism
        kernel(Group): the kernel of the homomorphism
    '''

    def __init__(self, mapping: dict, domain: Group, codomain: Group, name: str):
        if not isinstance(domain, Group) or not isinstance(codomain, Group):
            raise TypeError('domain and codomain must be of type Group')
        super().__init__(mapping, domain, codomain, name)

    def __matmul__(self, other):
        '''Create a new function from the composition self . other'''
        mapping = {k: self.mapping[other.mapping[k]] for k in other.mapping}
        return GroupFunction(mapping, other.domain, self.codomain, '{}@{}'.format(self.name, other.name))

    @property
    def inverse(self):
        '''Create a new function which is the inverse of this one'''
        if not self.is_bijective:
            raise ValueError('this function is not invertible')
        mapping = {v: k for k, v in self.mapping.items()}
        return GroupFunction(mapping, self.codomain, self.domain, '~{}'.format(self.name))

    @property
    def is_homomorphism(self):
        '''Check whether a function between groups is a homomorphism'''
        pairs = itertools.product(self.domain, repeat=2)
        if not all([self(first * second) == self(first) * self(second) for first, second in pairs]):
            return False
        return True

    @property
    def is_isomorphism(self):
        '''Check whether a function between groups is an isomorphism'''
        # Check that the function is bijective
        if not self.is_bijective:
            return False
        # Check that the function is a homomorphism
        if not self.is_homomorphism:
            return False
        # Check that the function's inverse is a homomorphism
        if not self.inverse.is_homomorphism:
            return False
        return True

    @property
    def kernel(self):
        '''The kernel of the homomorphism'''
        ker_set = Set()
        # Loop through all elements of the domain
        for element in self.domain:
            # Check whether each element gets mapped to the identity in the codomain
            if self(element) == self.codomain.identity:
                ker_set.add(element.value)
        # Filter the domain's product for the kernel
        ker_product = {(a, b): c for (a, b), c in self.domain.products.items() if a in ker_set and b in ker_set}
        ker = Group(ker_set, ker_product, 'ker({})'.format(self.name))
        return ker