from __future__ import absolute_import
import random
import six
from six.moves import range


class ChainLink(object):
    __slots__ = ["n", "tokens"]

    def __init__(self, tokens, n=0):
        self.n = n
        self.tokens = tokens

    def incr(self):
        self.n += 1

    def __str__(self):
        return '  %d: %s' % (self.n, ' '.join(self.tokens))


class Chain(object):
    __slots__ = ["n", "links"]

    def __init__(self):
        self.n = 0
        self.links = dict()

    def __str__(self):
        return '%d total:\n%s' % (self.n, '\n'.join([str(cl) for cl in self.links.values()]))

    def add(self, tokens):
        self.n += 1
        if tokens not in self.links:
            self.links[tokens] = ChainLink(tokens)
        self.links[tokens].incr()

    def addlink(self, chainlink):
        self.n += chainlink.n
        self.links[chainlink.tokens] = chainlink

    def choose(self):
        seek = random.randrange(0, self.n)
        for link in self.links.values():
            seek -= link.n
            if seek <= 0:
                return link.tokens

    def tolist(self):
        return [
            [cl.n, list(cl.tokens)]
            for
            cl
            in
            self.links.values()
        ]

    @classmethod
    def fromlist(cls, d):
        o = cls()

        for cll in d:
            o.addlink(ChainLink(tuple(cll[1]), n=cll[0]))
        return o


class Markov(object):

    """
    M is the number of tokens per inbound prediction
    N is the number of tokens in the outbound output
    """

    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.state = {}

    def __str__(self):
        return 'markov %d -> %d\n%s' % (self.m, self.n, '\n'.join(['%s: %s' % (self.detokenize(itok), c) for (itok, c) in self.state.items()]))

    def todict(self):
        return {
            'm': self.m,
            'n': self.n,
            'chains': [
                [list(intokens), chain.tolist()]
                for
                (intokens, chain)
                in
                self.state.items()
            ]
        }

    @classmethod
    def fromdict(cls, d):
        o = cls(d['m'], d['n'])
        for (intokenl, cl) in d['chains']:
            tokens = tuple(intokenl)
            o.state[tokens] = Chain.fromlist(cl)
        return o

    def tokenize(self, tokens):
        """
        Given a string or a tuple of tokens, if it's a string split it by spaces.
        :param tokens:
        :return: tuple of strings
        """
        if isinstance(tokens, six.string_types):
            tokens = tuple(tokens.split(' '))
        return tokens

    def teach(self, tokens):
        """
        Given some text or a tokenized sequence, teach the markov chain.
        :param tokens: either a string or a tuple of strings. If given as a string, it will be tokenized and then used.
        :return: None
        """
        tokens = self.tokenize(tokens)
        for i in range(len(tokens) + 1 - self.m - self.n):
            mi = i
            ni = mi + self.m
            inbound_key = tokens[mi:mi + self.m]
            outbound_key = tokens[ni:ni + self.n]

            if inbound_key not in self.state:
                self.state[inbound_key] = Chain()
            self.state[inbound_key].add(outbound_key)

    # if continued > 0, then we assume that n >= m
    def _choose(self, tokens, continued=0):
        tokens = self.tokenize(tokens)
        ns = list(range(len(tokens) + 1 - self.m))
        random.shuffle(ns)
        for i in ns:
            ik = tokens[i:i + self.m]
            if ik in self.state:
                c = self.state[ik].choose()
                if c:
                    if continued < 1:
                        return c
                    else:
                        nc = self._choose(c[-self.m:], continued=continued - 1)
                        if nc is None:
                            return c
                        return c + nc

    def choose(self, *a, **kw):
        return self.detokenize(self._choose(*a, **kw))

    def detokenize(self, tokens):
        if tokens is None:
            return None
        return ' '.join(list(tokens))
