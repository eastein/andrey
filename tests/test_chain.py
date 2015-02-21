import unittest
import andrey


class MarkovTests(unittest.TestCase):

    def test_1chain(self):
        m = andrey.Markov(1, 1)
        m.teach('a b c d')
        self.assertEquals('b c', m.choose('a', continued=1))

    def test_2chain(self):
        m = andrey.Markov(2, 2)
        m.teach('a b c d')
        m.teach('b c ddd ddd')
        self.assertEquals('c d', m.choose('a b', continued=0))

    def test_todict(self):
        m = andrey.Markov(1, 1)
        m.teach('a b c')
        self.assertEquals({
            'm': 1,
            'n': 1,
            'chains': [
                [['a'], [[1, ['b']]]],
                [['b'], [[1, ['c']]]],
            ]
        }, m.todict())

    def test_1chain_simplerestore(self):
        m = andrey.Markov(1, 1)
        m.teach('a b c d')
        m2 = andrey.Markov.fromdict(m.todict())
        self.assertEquals('b c', m2.choose('a', continued=1))
