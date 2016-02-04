from __future__ import absolute_import
import unittest
from andrey import andrey
import pprint
import msgpack
import io


class MarkovTests(unittest.TestCase):

    def test_1chain(self):
        m = andrey.Markov(1, 1)
        m.teach('alpha beta conky diagram')
        self.assertEqual('beta conky', m.choose('alpha', continued=1))

    def test_2chain(self):
        m = andrey.Markov(2, 2)
        m.teach('a b c d')
        m.teach('b c ddd ddd')
        self.assertEqual('c d', m.choose('a b', continued=0))

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
        self.assertEqual(sorted(mock.keys()), sorted(actual.keys()))
        self.assertEqual(sorted(mock['chains']), sorted(actual['chains']))

    def test_1chain_simplerestore(self):
        m = andrey.Markov(1, 1)
        m.teach('alpha beta conky delta')
        dump = msgpack.dumps(m.todict())
        dic = msgpack.unpack(io.BytesIO(dump), encoding='utf-8')
        m2 = andrey.Markov.fromdict(dic)
        self.assertEqual('beta conky', m2.choose('alpha', continued=1))
