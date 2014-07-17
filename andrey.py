import random

class ChainLink(object) :
	def __init__(self, tokens) :
		self.n = 0
		self.tokens = tokens

	def incr(self) :
		self.n += 1

class Chain(object) :
	def __init__(self) :
		self.n = 0
		self.links = dict()

	def add(self, tokens) :
		self.n += 1
		if tokens not in self.links :
			self.links[tokens] = ChainLink(tokens)
		self.links[tokens].incr()

	def choose(self) :
		seek = random.randrange(0, self.n)
		for link in self.links.values() :
			seek -= link.n
			if seek <= 0 :
				return link.tokens

class Markov(object) :
	"""
	M is the number of tokens per inbound prediction
	N is the number of tokens in the outbound output
	"""
	

	def __init__(self, m, n) :
		self.m = m
		self.n = n
		self.state = {}



	def tokenize(self, tokens) :
		if tokens.__class__ == str :
			tokens = tuple(tokens.split(' '))
		return tokens

	def teach(self, tokens) :
		tokens = self.tokenize(tokens)
		for i in range(len(tokens) + 1 - self.m - self.n) :
			mi = i
			ni = mi + self.m
			inbound_key = tokens[mi:mi+self.m]
			outbound_key = tokens[ni:ni+self.n]

			if inbound_key not in self.state :
				self.state[inbound_key] = Chain()
			self.state[inbound_key].add(outbound_key)

	# if continued > 0, then we assume that n >= m
	def _choose(self, tokens, continued=0) :
		tokens = self.tokenize(tokens)
		ns = range(len(tokens) + 1 - self.m)
		random.shuffle(ns)
		for i in ns :
			ik = tokens[i:i+self.m]
			if ik in self.state :
				c = self.state[ik].choose()
				if c :
					if continued < 1 :
						return c
					else :
						nc = self._choose(c[-self.m:], continued=continued-1)
						if nc is None :
							return c
						return c + nc

	def choose(self, *a, **kw) :
		return self.detokenize(self._choose(*a, **kw))

	def detokenize(self, tokens) :
		return ' '.join(list(tokens))
