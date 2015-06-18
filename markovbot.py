#!/usr/bin/env python

import sys
import mediorc
import time
import optparse
import random
import persist
import msgpack
import os.path

SAVE_WINDOW = 300.0


def wordprocess(s, repl=None):
    if repl is None:
        return s
    repl_w = repl['w']
    if 'p' in repl:
        if random.random() > repl['p']:
            return s

    if isinstance(repl_w, list):
        repl_w = random.choice(repl_w)
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
    return '%s%s' % (repl_w, rhs)


class MarkovBot(mediorc.IRC):

    def __init__(self, *a, **kw):
        mediorc.IRC.__init__(self, *(a[0:3]), **kw)
        if len(a) > 3:
            for line in open(a[3]):
                self.m.teach(line)

    def set_markov(self, m):
        self.m = m

    def save_markov(self):
        """
        If the markov chain has not been saved for SAVE_WINDOW time, save it.
        If no filename is configured on the bot, do not save.
        :return: None
        """
        if not self.filename:
            return

        now = time.time()

        if not hasattr(self, 'saved_at'):
            self.saved_at = now
        elif self.saved_at < (now - SAVE_WINDOW):
            self.m.save(self.filename)
            self.saved_at = now

        self.saved_at = now

    def on_pubmsg(self, c, e):
        chan = e.target
        txt = e.arguments[0]

        def output_filtering(r):
            return ' '.join([wordprocess(s, repl=self.word_replace) for s in r.split(' ')])

        def generate(txt, attempts=1, acceptance_test=None):
            def generate_inner(txt):
                return self.m.choose(txt, continued=10)
            if not acceptance_test:
                return generate_inner(txt)
            else:
                for i in range(attempts):
                    r = generate_inner(txt)
                    if acceptance_test(r):
                        return r

        def filter_test(r):
            if r is None:
                return False
            do_send = False
            rlower = r.lower()
            for word in self.word_filter:
                if word.lower() in rlower:
                    do_send = True
                    break
            return do_send

        if random.random() < self.ratio:
            if self.word_filter:
                r = generate(txt, attempts=50, acceptance_test=filter_test)
            else:
                r = generate(txt)

            if r:
                r = output_filtering(r)
                self.connection.privmsg(chan, r)

        self.m.teach(txt)
        self.save_markov()


class MarkovThread(mediorc.IRCThread):
    def __init__(self, args, filename=None, ratio=None, word_replace=None, word_filter=None):
        self.a = args
        self.filename = filename
        self.ratio = ratio
        self.word_replace = word_replace
        self.word_filter = word_filter

        load = False
        if filename:
            if os.path.exists(filename):
                load = True
        if not load:
            self.m = persist.PersistedMarkov(2, 3)
        else:
            self.m = persist.PersistedMarkov.restore(filename, 2, 3)

        mediorc.IRCThread.__init__(self)

    def bot_create(self):
        mb = MarkovBot(*(self.a))
        mb.set_markov(self.m)
        mb.filename = self.filename
        mb.ratio = self.ratio
        mb.word_replace = self.word_replace
        mb.word_filter = self.word_filter
        return mb

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest='file', default=None,
                      help="File to store markov chain in. Will also use filenames with incomplete suffixes during write.")
    parser.add_option('-r', '--ratio', dest='ratio', default='0.008',
                      help='Probablity that the bot will attempt to respond to any given line of chat.')
    parser.add_option('--word-replace', dest='word_replace', default=None,
                      help='Comma separated (no whitespace) list of words to replace every word with (except for punctuation, plurals, gerunds...')
    parser.add_option('--word-filter', dest='word_filter', default=None,
                      help='Comma separated (no whitespace) list of words to filter by; only talk if one of these words is in the text the bot would say.')
    parser.add_option('--replace-probability', dest='replace_probability', default=1.0,
                      help="When word replace in use, replace words with only this probability.")

    (options, args) = parser.parse_args()

    word_replace = options.word_replace
    if word_replace is not None:
        word_replace = {
            'w': word_replace.split(','),
            'p': float(options.replace_probability)
        }
    word_filter = options.word_filter
    if word_filter is not None:
        word_filter = word_filter.split(',')

    try:
        s = MarkovThread(args, filename=options.file,
                         ratio=float(options.ratio), word_replace=word_replace, word_filter=word_filter)
    except IndexError:
        print 'Bad parameters. For usage, use markovboy.py -h.'
        sys.exit(1)

    s.run()
