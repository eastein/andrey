#!/usr/bin/env python

import sys
import mediorc
import time
import optparse
import random
import andrey
import msgpack
import os.path

SAVE_WINDOW = 10.0


def wordprocess(s, repl=None):
    if repl is None:
        return s
    if isinstance(repl, list):
        repl = random.choice(repl)
    keep = ['"', "'", ',', ';', ':', '!', '?', '.', 'ing', 's']
    rhs = ''
    found = True
    while found and s:
        found = False
        for k in keep:
            if s.endswith(k):
                s = s[0:len(s) - len(k)]
                rhs = '%s%s' % (k, rhs)
                found = True
    return '%s%s' % (repl, rhs)


class MarkovBot(mediorc.IRC):

    def __init__(self, *a, **kw):
        mediorc.IRC.__init__(self, *(a[0:3]), **kw)
        if len(a) > 3:
            for line in open(a[3]):
                self.m.teach(line)

    def set_markov(self, m):
        self.m = m

    def save_markov(self):
        # nah
        if not self.filename:
            return

        now = time.time()

        if not hasattr(self.m, 'saved_at'):
            self.m.saved_at = now
        elif self.m.saved_at < (now - SAVE_WINDOW):
            tfn = '%s.inprog-%d' % (self.filename, random.randint(1, 1000000))
            fh = open(tfn, 'w')
            ok = False
            try:
                msgpack.dump(self.m.todict(), fh)
                ok = True
            finally:
                fh.close()

            if ok:
                if os.path.exists(self.filename):
                    os.rename(self.filename, '%s.bak' % self.filename)
                os.rename(tfn, self.filename)
                self.m.saved_at = now

    def on_pubmsg(self, c, e):
        chan = e.target
        txt = e.arguments[0]

        if random.random() < self.ratio:
            r = self.m.choose(txt, continued=10)
            if r:
                r = ' '.join([wordprocess(s, repl=self.word_replace)
                              for s in r.split(' ')])
                self.connection.privmsg(chan, r)

        self.m.teach(txt)
        self.save_markov()


class MarkovThread(mediorc.IRCThread):
    def __init__(self, args, filename=None, ratio=None, word_replace=None):
        self.a = args
        self.filename = filename
        self.ratio = ratio
        self.word_replace = word_replace

        load = False
        if filename:
            if os.path.exists(filename):
                load = True
        if not load:
            self.m = andrey.Markov(2, 3)
        else:
            self.m = andrey.Markov.fromdict(msgpack.load(open(filename)))

        mediorc.IRCThread.__init__(self)

    def bot_create(self):
        mb = MarkovBot(*(self.a))
        mb.set_markov(self.m)
        mb.filename = self.filename
        mb.ratio = self.ratio
        mb.word_replace = self.word_replace
        return mb

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest='file', default=None,
                      help="File to store markov chain in. Will also use filenames with incomplete suffixes during write.")
    parser.add_option('-r', '--ratio', dest='ratio', default='0.008',
                      help='Probablity that the bot will attempt to respond to any given line of chat.')
    parser.add_option('--word-replace', dest='word_replace', default=None,
                      help='Comma separated (no whitespace) list of words to replace every word with (except for punctuation, plurals, gerunds...')

    (options, args) = parser.parse_args()

    word_replace = options.word_replace
    if word_replace is not None:
        word_replace = word_replace.split(',')

    try:
        s = MarkovThread(args, filename=options.file,
                         ratio=float(options.ratio), word_replace=word_replace)
    except IndexError:
        print 'Bad parameters. For usage, use markovboy.py -h.'
        sys.exit(1)

    s.run()
