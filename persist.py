import random
import os.path
import msgpack
import andrey


class PersistedMarkov(andrey.Markov):

    def save(self, filename):
        tfn = '%s.inprog-%d' % (filename, random.randint(1, 10000000))
        fh = open(tfn, 'w')

        try:
            msgpack.dump(self.todict(), fh)
        finally:
            fh.close()

            if os.path.exists(filename):
                os.rename(filename, '%s.bak' % filename)
            os.rename(tfn, filename)

    @classmethod
    def restore(cls, filename, *a, **kw):
        """
        If file exists, load and ignore other parameters. If file does not exist, create using parameters.
        :param filename: filename to attempt to load from
        :param a: arguments to andrey.Markov constructor
        :param kw: keyword arguments to andrey.Markov constructor
        :return: andrey.Markov.PersistedMarkov instance
        """
        if not os.path.exists(filename):
            return cls(*a, **kw)
        else:
            return cls.fromdict(msgpack.load(open(filename)))