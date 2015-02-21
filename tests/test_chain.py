import unittest
import andrey

class MarkovTests(unittest.TestCase) :
    def test_1chain(self) :
        m = andrey.Markov(1, 1)
        m.teach('a b c d')
        self.assertEquals('b c', m.choose('a', continued=1))

    def test_2chain(self) :
        m = andrey.Markov(2, 2)
        m.teach('a b c d')
        m.teach('b c ddd ddd')
        self.assertEquals('c d', m.choose('a b', continued=0))
