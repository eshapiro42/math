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
        return 'Set({})'.format(', '.join(map(repr, self.elements)))

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