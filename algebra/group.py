'''Classes for groups and functions between them'''

import collections
import itertools

from common import (
    Function,
    Set,
)


class Group(Set):
    '''Group

    Attributes:
        products (dict): a mapping of pairs of elements to their product
    '''

    def __init__(self, group_set: Set, products: dict) -> None:
        super().__init__(*group_set)
        self._products = products
        if not self.closed_under_products:
            raise ValueError('not closed under products')
        self._identity = self.identity
        if self._identity is None:
            raise ValueError('there is no identity element')
        self._inverses = self.inverses
        if self._inverses is None:
            raise ValueError('not closed under inverses')
        if not self.is_associative:
            raise ValueError('not associative')
    
    def __repr__(self):
        return 'Group({})'.format(', '.join(map(repr, self.elements)))

    @property
    def products(self) -> dict:
        return self._products
        
    @property
    def closed_under_products(self) -> bool:
        '''Check for closure under products'''
        # Check that nothing is included that is not in the group
        for (factor1, factor2), product in self._products.items():
            if not all([element in self for element in [factor1, factor2, product]]):
                return False
        # Check that everything in the group is accounted for
        for pair in itertools.product(self, repeat=2):
            if pair not in self._products:
                return False
        return True

    @property
    def identity(self) -> bool:
        '''Check for an identity element'''
        # loop through each element to see if it is the identity
        for candidate in self:
            # Check its product with all elements to see if it's always absorbed
            if all([
                    self._products[(candidate, other)] == self._products[(other, candidate)] == other
                    for other in self
            ]):
                return candidate
        return None

    @property
    def inverses(self) -> bool:
        '''Find inverses for each element'''
        inverses = {}
        # Loop through each element
        for element in self:
            # If we've already found element to be the inverse of something
            if element in inverses.values():
                # That something is the inverse of element
                inverses[element] = list(inverses.keys())[list(inverses.values()).index(element)]
                continue
            # Otherwise, we need to look for its inverse
            for other in self:
                if self._products[(element, other)] == self._identity:
                    inverses[element] = other
                    break
            else:
                # If we got here, no inverse was found for element
                return None
        # If we got here, an inverse was found for every element
        return inverses

    @property
    def is_associative(self) -> bool:
        '''Check that the group operation is associative'''
        triples = itertools.product(self, repeat=3)
        for a, b, c in triples:
            if self._products[(self._products[(a, b)], c)] != self._products[(a, self._products[(b, c)])]:
                return False
        return True

    @property
    def is_abelian(self) -> bool:
        '''Check that the group is commutative'''
        pairs = itertools.combinations(self, 2)
        if not all([self._products[(a, b)] == self._products[(b, a)] for a, b in pairs]):
            return False
        return True
 
    def inverse(self, element):
        '''Get the inverse of a group element'''
        return self._inverses[element]

    def order(self, element=None):
        '''Get the order of the group or one of its elements'''
        # If no element is specified, return the order of the group
        if element is None:
            return len(self)
        # By Lagrange's Theorem, the order of an element divides the order of the (finite) group
        for candidate, _ in enumerate(self, start=1):
            if self(*[element] * candidate) == self._identity:
                return candidate

    def subproduct(self, subgroup_set: Set) -> dict:
        '''Get inherited group product for a subgroup'''
        pairs = list(itertools.product(subgroup_set, repeat=2))
        subgroup_product = {pair: product for pair, product in self._products.items() if pair in pairs}
        return subgroup_product

    def subgroup(self, subgroup_set: Set):
        '''Create a subgroup from a subset'''
        # First verify that it's actually a subset
        if not subgroup_set <= self.elements:
            raise ValueError('not a subset')
        # Get the inherited group product
        subgroup_product = self.subproduct(subgroup_set)
        # Try to build the subgroup
        subgroup = Group(subgroup_set, subgroup_product)
        return subgroup

    def is_normal(self, subgroup) -> bool:
        '''Check whether a subgroup is normal'''
        # First verify that it's actually a subgroup
        if not subgroup <= self:
            raise ValueError('not a subgroup')
        # If we're in an abelian group, every subgroup is normal
        if self.is_abelian:
            return True
        # Loop through elements of the subgroup
        for element in subgroup:
            # Check that all congugates of element are in the subgroup
            if not all([self(other, element, self.inverse(other)) in subgroup for other in self]):
                return False
        return True

    def left_coset(self, element, subgroup):
        '''Get the left coset element + subgroup'''
        # Check that subgroup is actually a subgroup
        if not subgroup <= self:
            raise ValueError('not a subgroup')
        # Construct the coset
        coset = Set(*[self(element, s) for s in subgroup])
        return coset

    def right_coset(self, subgroup, element):
        '''Get the right coset subgroup + element'''
        # Check that subgroup is actually a subgroup
        if not subgroup <= self:
            raise ValueError('not a subgroup')
        # Construct the coset
        coset = Set(*[self(s, element) for s in subgroup])
        return coset

    def coset(self, subgroup, element):
        '''Get the coset subgroup + element

        Note this only works for normal subgroups. 
        Otherwise left and right cosets are not equal.
        '''
        if not self.is_normal(subgroup):
            raise ValueError('not a normal subgroup so left and right cosets are distinct')
        return self.right_coset(subgroup, element)

    def quotient(self, normal_subgroup):
        '''Get the quotient group modulo a subgroup
        
        Note that this only works for normal subgroups.
        '''
        if not self.is_normal(normal_subgroup):
            raise ValueError('not a normal subgroup so quotient group is not well defined')
        # The quotient set consists of all cosets of normal_subgroup
        quotient_set = Set()
        for element in self:
            coset = self.coset(normal_subgroup, element)
            if coset not in quotient_set:
                quotient_set.add(coset)
        # The quotient product takes cosets wrt a and b and returns the coset wrt a*b
        quotient_product = {}
        for a, b in itertools.product(self, repeat=2):
            coset_a = self.coset(normal_subgroup, a)
            coset_b = self.coset(normal_subgroup, b)
            if (coset_a, coset_b) not in quotient_product:
                coset_ab = self.coset(normal_subgroup, self(a, b))
                quotient_product[(coset_a, coset_b)] = coset_ab
        # Construct the quotient group
        quotient = Group(quotient_set, quotient_product)
        return quotient

    @property
    def center(self):
        '''Get the center of a group'''
        center_set = Set(*[element for element in self if all([self(element, other) == self(other, element) for other in self])])
        center = self.subgroup(center_set)
        return center

    @property
    def commutator_subgroup(self):
        '''Get the commutator subgroup of a group'''
        pairs = itertools.product(self, repeat=2)
        commutator_subgroup_set = Set(*[self(self.inverse(a), self.inverse(b), a, b) for a, b in pairs])
        commutator_subgroup = self.subgroup(commutator_subgroup_set)
        return commutator_subgroup

    @property
    def abelianization(self):
        '''Get the abelianization of a group'''
        return self.quotient(self.commutator_subgroup)

    def __call__(self, *elements):
        '''Compute the product of elements'''
        product = self._identity
        for element in elements:
            if element not in self:
                raise ValueError('{} is not a group element'.format(element))
            product = self._products[(product, element)]
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
        return super().__eq__(other) and self._products == other._products
    
    def __le__(self, other) -> bool:
        '''Check whether a group is a subgroup of another'''
        # By Lagrange's Theorem, if ord(self) does not divide ord(order) then it can't be a subgroup
        if not other.order() % self.order() == 0:
            return False
        # Self is a subgroup of other if it is a subset and
        # its product dictionary is a subdictionary of other's
        return super().__le__(other) and all([item in other._products.items() for item in self._products.items()])

    def __lt__(self, other) -> bool:
        '''Check whether a group is a proper subgroup of another'''
        # By Lagrange's Theorem, if ord(self) does not divide ord(order) then it can't be a subgroup
        if not other.order() % self.order() == 0:
            return False
        # Self is a proper subgroup of other if it is a proper subset and
        # its product dictionary is a subdictionary of other's
        return super().__lt__(other) and all([item in other._products.items() for item in self._products.items()])

    def __ge__(self, other) -> bool:
        '''Check whether a group is a supergroup of another'''
        # By Lagrange's Theorem, if ord(other) does not divide ord(self) then it can't be a supergroup
        if not self.order() % other.order() == 0:
            return False
        # Self is a supergroup of other if it is a superset and
        # its product dictionary is a superdictionary of other's
        return super().__ge__(other) and all([item in self._products.items() for item in other._products.items()])

    def __gt__(self, other) -> bool:
        '''Check whether a group is a proper supergroup of another'''
        # By Lagrange's Theorem, if ord(other) does not divide ord(self) then it can't be a supergroup
        if not self.order() % other.order() == 0:
            return False
        # Self is a proper supergroup of other if it is a superset and
        # its product dictionary is a superdictionary of other's
        return super().__gt__(other) and all([item in self._products.items() for item in other._products.items()])


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
    def is_homomorphism(self):
        '''Check whether a function between groups is a homomorphism'''
        pairs = itertools.product(self.domain, repeat=2)
        if not all([self(self.domain(a, b)) == self.codomain(self(a), self(b)) for a, b in pairs]):
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
                ker_set.add(element)
        # Filter the domain's product for the kernel
        ker_product = {(a, b): c for (a, b), c in self.domain.products.items() if a in ker_set and b in ker_set}
        ker = Group(ker_set, ker_product)
        return ker