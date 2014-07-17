#!/usr/bin/env python

import sys
import mediorc
import time
import optparse
import random
import andrey

p = 0.008



class MarkovBot(mediorc.IRC) :
	def __init__(self, *a, **kw) :
		mediorc.IRC.__init__(self, *a, **kw)
		self.m = andrey.Markov(2,3)

	def on_pubmsg(self, c, e) :
		chan = e.target()
		txt = e.arguments()[0]

		if random.random() < p :
			r = self.m.choose(txt, continued=10))
			if r :
				self.connection.privmsg(chan, r)
		
		self.m.teach(txt)

class MarkovThread(mediorc.IRCThread) :
	def __init__(self, server, nick, chan):
		self.bot_create = lambda: MarkovBot(server, nick, chan)
		mediorc.IRCThread.__init__(self)

if __name__ == '__main__' :
	parser = optparse.OptionParser()

	(options, args) = parser.parse_args()

	try :
		s = MarkovThread(args[0], args[1], args[2])
	except IndexError :
		print 'usage: markovbot.py server nick channel'
		sys.exit(1)
	
	# threading,? NOPE
	s.run()
