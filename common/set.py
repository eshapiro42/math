import collections
import itertools

class Set(collections.MutableSet, collections.Hashable):
    def __init__(self, *elements):
        self.elements = set()
        for value in elements:
            self.elements.add(value)
            
    def add(self, element):
        return self.elements.add(element)
        
    def discard(self, element):
        return self.elements.remove(element)
            
    def __hash__(self):
        return super()._hash()

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, value):
        return value in self.elements

    def __len__(self):
        return len(self.elements)
        
    def __str__(self):
        return '{{{}}}'.format(', '.join(map(str, self.elements)))
    
    def __repr__(self):
        return '{{{}}}'.format(', '.join(map(str, self.elements)))
#         return 'Set({})'.format(', '.join(map(repr, self.elements)))

    def __sub__(self, other):
        return Set(*(self.elements.difference(other.elements)))
    
    def __add__(self, other):
        return self.union(other)
    
    def difference(self, other):
        return self - other

    def union(self, other):
        return Set(*(self.elements.union(other.elements)))
    
    def intersection(self, other):
        return Set(*(self.elements.intersection(other.elements)))
    
    def issubset(self, other):
        return self.elements.issubset(other.elements)

    @property
    def powerset(self):
        powerset = Set(Set())
        for length, _ in enumerate(self, start=1):
            for combination in itertools.combinations(self, length):
                powerset.add(Set(*combination))
        return powerset
    
    @classmethod
    def _from_iterable(cls, iterable):
        return cls(*iterable)
    
    @staticmethod
    def unions(*sets):
        union = Set()
        for s in sets:
            union = union + s
        return union
    
    def is_sigma_algebra(self, X):
        try:
            # {} and X must be in any sigma algebra
            assert Set() in self
            assert X in self
            # a sigma algebra is closed under complements
            for s in self:
                assert X - s in self
            # a sigma algebra is closed under (countable) unions
            for length in range(len(X)):
                for combination in itertools.combinations(self, length):
                    assert self.unions(Set(*combination)).issubset(self)
        except AssertionError:
            return False
        else:
            return True