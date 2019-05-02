from .set import Set


class Function:
    '''Function (mapping between Sets)

    Attributes:
        mapping (dict): value, image pairs (basically {x: f(x) for x in domain})
        domain (Set): the function's domain
        codomain (Set): the function's codomain

    Properties:
        inverse (Function): the function's inverse, if it has one
        is_injective (bool): whether the function is injective
        is_surjective (bool): whether the function is surjective
        is_bijective (bool): whether the function is bijective
    '''

    def __init__(self, mapping: dict, domain: Set, codomain: Set, name=None) -> None:
        # Check that all elements of the domain get mapped
        if not all([point in mapping.keys() for point in domain]):
            raise ValueError('all values in the domain must get mapped')
        # Check that everything in the mapping is valid
        for key, val in mapping.items():
            if key not in domain:
                raise ValueError('value {} is not in the domain'.format(key))
            if val not in codomain:
                raise ValueError('value {} is not in the codomain'.format(val))
        self.mapping = mapping
        self.domain = domain
        self.codomain = codomain
        self.name = name

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

    @property
    def inverse(self):
        '''Create a new function which is the inverse of this one'''
        if not self.is_bijective:
            raise ValueError('this function is not invertible')
        mapping = {v: k for k, v in self.mapping.items()}
        return Function(mapping, self.codomain, self.domain)

    def fiber(self, value):
        '''Get the preimage of a single value in the codomain'''
        if value not in self.codomain:
            raise ValueError('{} is not in the codomain'.format(value))
        fiber = Set(*[k for k in self.mapping if self.mapping[k] == value])
        return fiber

    def preimage(self, subset: Set):
        '''Get the preimage of a subset of the codomain'''
        if not subset <= self.codomain:
            raise ValueError('{} if not a subset of the codomain'.format(subset))
        preimage = Set()
        for value in subset:
            preimage |= self.fiber(value)
        return preimage

    def image(self, subset: Set):
        '''Take the image of a subset under the function'''
        image = Set()
        for value in subset:
            image.add(self(value))
        return image

    @property
    def is_injective(self):
        '''Check whether the function is an injection'''
        return all([len(self.fiber(v)) == 1 for v in self.mapping.values()])

    @property
    def is_surjective(self):
        '''Check whether the function is a surjection'''
        return all([v in self.mapping.values() for v in self.codomain])

    @property
    def is_bijective(self):
        '''Check whether the function is a bijection'''
        return self.is_injective and self.is_surjective
