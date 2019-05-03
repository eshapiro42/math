from sympy import isprime
from .group import *


class Zn:
    '''Additive Group of Integers Modulo n'''
    def __init__(self, n):
        self.Zn_set = Set(*range(n))
        self.Zn_products = {(a, b): (a + b) % n for a, b in itertools.product(self.Zn_set, repeat=2)}
        self.Zn = Group(self.Zn_set, self.Zn_products)


class Mp:
    '''Multiplicative Group of Integers Modulo a Prime p'''
    def __init__(self, p):
        if not isprime(p):
            raise ValueError('modulus is not prime')
        self.Mp_set = Set(*range(1, p))
        self.Mp_products = {(a, b): (a * b) % p for a, b in itertools.product(self.Mp_set, repeat=2)}
        self.Mp = Group(self.Mp_set, self.Mp_products)


class D3:
    '''Dihedral Group of Order 6 — Smallest non-abelian group'''

    e = 'e'
    a = 'a'
    b = 'b'
    c = 'c'
    d = 'd'
    f = 'f'

    D3_set = Set(e, a, b, c, d, f)
    D3_products = {
        (e, e): e, (e, a): a, (e, b): b, (e, c): c, (e, d): d, (e, f): f, 
        (a, e): a, (a, a): e, (a, b): d, (a, c): f, (a, d): b, (a, f): c,
        (b, e): b, (b, a): f, (b, b): e, (b, c): d, (b, d): c, (b, f): a,
        (c, e): c, (c, a): d, (c, b): f, (c, c): e, (c, d): a, (c, f): b,
        (d, e): d, (d, a): c, (d, b): a, (d, c): b, (d, d): f, (d, f): e,
        (f, e): f, (f, a): b, (f, b): c, (f, c): a, (f, d): e, (f, f): d,
    }
    D3 = Group(D3_set, D3_products)


