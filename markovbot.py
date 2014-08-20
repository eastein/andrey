#!/usr/bin/env python

import sys
import mediorc
import time
import optparse
import random
import andrey


#p=1
p = 0.4
wordreplace = ['duck', 'quack', 'squawk', 'bread']
wordreplace = None

def wordprocess(s, repl=wordreplace) :
	if repl is None :
		return s
	if isinstance(repl, list) :
		repl = random.choice(repl)
	keep = ['"', "'", ',', ';', ':', '!', '?', '.', 'ing', 's']
	rhs = ''
	found = True
	while found and s :
		found = False
		for k in keep :
			if s.endswith(k) :
				s = s[0:len(s)-len(k)]
				rhs = '%s%s' % (k, rhs)
				found = True
	return '%s%s' % (repl, rhs)

class MarkovBot(mediorc.IRC) :
	def __init__(self, *a, **kw) :
		mediorc.IRC.__init__(self, *(a[0:3]), **kw)
		self.m = andrey.Markov(2,3)
		if len(a) > 3 :
			for line in open(a[3]) :
				self.m.teach(line)

	def on_pubmsg(self, c, e) :
		chan = e.target()
		txt = e.arguments()[0]

		if random.random() < p :
			r = self.m.choose(txt, continued=10)
			if r :
				r = ' '.join([wordprocess(s) for s in r.split(' ')])
				self.connection.privmsg(chan, r)
		
		#self.m.teach(txt)

class MarkovThread(mediorc.IRCThread) :
	def __init__(self, *a):
		self.bot_create = lambda: MarkovBot(*a)
		mediorc.IRCThread.__init__(self)

if __name__ == '__main__' :
	parser = optparse.OptionParser()

	(options, args) = parser.parse_args()

	try :
		s = MarkovThread(*args)
	except IndexError :
		print 'usage: markovbot.py server nick channel'
		sys.exit(1)
	
	# threading,? NOPE
	s.run()
