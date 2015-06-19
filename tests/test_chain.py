import unittest
import andrey
import pprint
import msgpack


class MarkovTests(unittest.TestCase):

    def test_1chain(self):
        m = andrey.Markov(1, 1)
        m.teach('alpha beta conky diagram')
        self.assertEquals('beta conky', m.choose('alpha', continued=1))

    def test_2chain(self):
        m = andrey.Markov(2, 2)
        m.teach('a b c d')
        m.teach('b c ddd ddd')
        self.assertEquals('c d', m.choose('a b', continued=0))

    def test_todict(self):
        m = andrey.Markov(1, 1)
        m.teach('alpha beta conky')
        # depends on the order that natural iteration of items() produces..
        # should redesign test
        mock = {
            'm': 1,
            'n': 1,
            'chains': [
                [['beta'], [[1, ['conky']]]],
                [['alpha'], [[1, ['beta']]]],
            ]
        }
        actual = m.todict()
        pprint.pprint(actual)
        self.assertEquals(mock, actual)

    def test_1chain_simplerestore(self):
        m = andrey.Markov(1, 1)
        m.teach('alpha beta conky delta')
        m2 = andrey.Markov.fromdict(msgpack.loads(msgpack.dumps(m.todict())))
        self.assertEquals('beta conky', m2.choose('alpha', continued=1))
