from sympy import isprime
from operator import attrgetter
from .group import *


class Zn:
    '''Additive Group of Integers Modulo n'''
    def __new__(cls, n):
        group_set = Set(*range(n))
        group_products = {(a, b): (a + b) % n for a, b in itertools.product(group_set, repeat=2)}
        group = Group(group_set, group_products)
        return group


class Mp:
    '''Multiplicative Group of Integers Modulo a Prime p'''
    def __new__(cls, p):
        if not isprime(p):
            raise ValueError('modulus is not prime')
        group_set = Set(*range(1, p))
        group_products = {(a, b): (a * b) % p for a, b in itertools.product(group_set, repeat=2)}
        group = Group(group_set, group_products)
        return group


class Dn:
    '''Dihedral Group of Order 2n'''
    def __new__(cls, n):
        r = ['r{}'.format(i) for i in range(n)]
        f = ['f{}'.format(i) for i in range(n)]

        group_set = Set(*(r + f))
        group_products = {}

        for i, j in itertools.product(range(0, n), repeat=2):
            group_products[r[i], r[j]] = r[(i + j) % n]
            group_products[r[i], f[j]] = f[(i + j) % n]
            group_products[f[i], r[j]] = f[(i - j) % n]
            group_products[f[i], f[j]] = r[(i - j) % n]

        group = Group(group_set, group_products)
        return group