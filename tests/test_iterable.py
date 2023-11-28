from unittest import TestCase
from collections import namedtuple
import itertools

from util.iterable import Comparative

def eq_chr(i, char):
    return chr(i) == char

class TestSets(TestCase):
    def test_sets(self):
        Params = namedtuple('Params', ['function_type', 'domain', 'codomain'])
        sets = itertools.product([Comparative.one_to_one, Comparative.bijection],
                                 [{0}, {1}, {0, 1}],
                                 [{'\x00'}, {'\x01'}, {'\x00', '\x01'}])
        sets = map(Params._make, sets)
        actuals = [s.function_type(s.domain, s.codomain) for s in sets]
        results = [True, False, True,
                   False, True, True,
                   False, False, True,
                   
                   True, False, False,
                   False, True, False,
                   False, False, True]
        for i in enumerate(sets):
            with self.subTest(f'{sets[i]} and {results[i]}'):
                self.assertEqual(actuals[i], results[i])
