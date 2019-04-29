import itertools

class Topology:
    def __init__(self, subsets):
        # Check that all subsets are of type set or frozenset
        if not all([isinstance(x, (set, frozenset)) for x in subsets]):
            raise TypeError('all elements of the topology must be sets')
        # Check pairwise unions
        unions, set1, set2 = self.pairwise_unions(subsets)
        if not unions:
            raise ValueError('{} and {} are in the topology but their union {} is not'.format(set1, set2, set1 | set2))
        # Check pairwise intersections
        intersections, set1, set2 = self.pairwise_intersections(subsets)
        if not intersections:
            raise ValueError('{} and {} are in the topology but their intersection {} is not'.format(set1, set2, set1 & set2))
        # Cast all subsets to frozensets so they are hashable
        self.subsets = set(map(frozenset, subsets))
        self.space = set()
        for openset in subsets:
            self.space |= openset
        
    def __mul__(self, other):
        # Create a basis from the cartesian products of subsets in self and other
        basis = [itertools.product(set1, set2) for set1 in self.subsets for set2 in other.subsets]
        # Create a topology from the basis
        product = Topology.fromBasis(list(map(set, basis)))
        return product
        
    def __eq__(self, other):
        return self.subsets == other.subsets
        
    @staticmethod
    def pairwise_unions(subsets):
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Make sure their union is in subsets
            if not set1 | set2 in subsets:
                return False, set1, set2
        return True, None, None
    
    @staticmethod
    def pairwise_intersections(subsets):
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Make sure their intersection is in subsets
            if not set1 & set2 in subsets:
                return False, set1, set2
        return True, None, None
    
    @staticmethod
    def closed(subsets):
        return Topology.pairwise_unions(subsets)[0] and Topology.pairwise_intersections(subsets)[0]
    
    @staticmethod
    def isBasis(subsets):
        # Loop through all distinct pairs of sets in subsets
        for set1, set2 in itertools.combinations(subsets, 2):
            # Compute their intersection
            intersection = set1 & set2
            # If the intersection is empty, we're fine
            if not intersection:
                continue
            # Otherwise, we need to make sure there's a basis subset contained in their intersection
            if not any(map(lambda x: x <= intersection, subsets)):
                return False, set1, set2
        return True, None, None

    @classmethod
    def fromMinimal(cls, base_subsets):
        # Check that all subsets are of type set or frozenset
        if not all([isinstance(x, (set, frozenset)) for x in base_subsets]):
            raise TypeError('all elements of the topology must be sets')
        # Add the empty set
        base_subsets.append(set())
        base_subsets = list(map(frozenset, base_subsets))
        subsets = base_subsets[:]
        # Loop through all distinct pairs of sets in base_subsets
        for idx1, set1 in enumerate(base_subsets):
            for offset, _ in enumerate(base_subsets[idx1:]):
                union = frozenset(set1.union(*base_subsets[idx1:idx1 + offset]))
                intersection = frozenset(set1.intersection(*base_subsets[idx1:idx1 + offset]))
                subsets.append(union)
                subsets.append(intersection)
        base_subsets = subsets
        # Create a topology from subsets
        top = cls(set(map(frozenset, subsets)))
        return top
    
    @classmethod
    def fromBasis(cls, base_subsets):
        # Check that all subsets are of type set or frozenset
        if not all([isinstance(x, (set, frozenset)) for x in base_subsets]):
            raise TypeError('all elements of the topology must be sets')
        # Check that base_subsets is actually a basis
        isbasis, set1, set2 = cls.isBasis(base_subsets)
        if not isbasis:
            raise ValueError('there is no basis set in the intersection of {} and {}'.format(set1, set2))
        # Add the empty set
        base_subsets.append(set())
        base_subsets = list(map(frozenset, base_subsets))
        subsets = base_subsets[:]
        # Loop through all distinct pairs of sets in base_subsets
        for idx1, set1 in enumerate(base_subsets):
            for offset, _ in enumerate(base_subsets[idx1:]):
                union = frozenset(set1.union(*base_subsets[idx1:idx1 + offset]))
                subsets.append(union)
            base_subsets = subsets
        # Create a topology from subsets
        top = cls(set(map(frozenset, subsets)))
        return top


class Function:
    def __init__(self, mapping, domain, codomain):
        # Check that all elements of the domain get mapped
        if not all([point in mapping.keys() for point in domain.space]):
            raise ValueError('all values in the domain must get mapped')
        # Check that everything in the mapping is valid
        for k, v in mapping.items():
            if k not in domain.space:
                raise ValueError('value {} is not in the domain'.format(k))
            if v not in codomain.space:
                raise ValueError('value {} is not in the codomain'.format(v))
        self.mapping = mapping
        self.domain = domain
        self.codomain = codomain
        
    def __call__(self, value):
        try:
            return self.mapping[value]
        except:
            raise ValueError('{} is not in the domain'.format(value))
            
    def __matmul__(self, other):
        self.mapping
        other.mapping
        mapping = {k: self.mapping[other.mapping[k]] for k in other.mapping}
        return Function(mapping, other.domain, self.codomain)
    
    def __eq__(self, other):
        return self.mapping == other.mapping
    
    def inverse(self):
        if not self.isBijective():
            raise ValueError('this function is not invertible')
        mapping = {v: k for k, v in self.mapping.items()}
        return Function(mapping, self.codomain, self.domain)
    
    def fiber(self, value):
        fiber = frozenset(k for k in self.mapping if self.mapping[k] == value)
        return fiber
    
    def preimage(self, subset):
        preimage = set()
        for value in subset:
            preimage |= self.fiber(value)
        return preimage
     
    def image(self, subset):
        im = set()
        for value in subset:
            im |= self(value)
        return im
    
    def isBijective(self):
        # Check for surjectivity
        if not all([v in self.mapping.values() for v in self.codomain.space]):
            return False
        # Check for injectivity
        if not all([len(self.fiber(v)) == 1 for v in self.mapping.values()]):
            return False
        return True
    
    def isContinuous(self):
        return all([self.preimage(openset) in self.domain.subsets for openset in self.codomain.subsets])