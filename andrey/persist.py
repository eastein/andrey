from __future__ import absolute_import
import random
import os.path
import msgpack
import andrey.markov


class PersistenceError(Exception):

    """
    Raised in cases where persistence experienced a problem.
    """


class NoSuchFileError(Exception):

    """
    Raised when you attempt to restore and did not provide default
    """


class PersistedMarkov(andrey.markov.Markov):

    def save(self, filename):
        tfn = '%s.inprog-%d' % (filename, random.randint(1, 10000000))
        fh = open(tfn, 'wb')

        try:
            me_as_dict = self.todict()
            msgpack.pack(me_as_dict, encoding='utf-8', stream=fh)
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
        :param a: arguments to andrey.markov.Markov constructor
        :param kw: keyword arguments to andrey.markov.Markov constructor
        :return: andrey.persist.PersistedMarkov instance
        """
        if not os.path.exists(filename):
            if not a:
                raise NoSuchFileError("You attempted to restore and did not supply parameters for andrey.Markov.")
            return cls(*a, **kw)
        else:
            with open(filename, 'rb') as fh:
                d = msgpack.unpack(fh, encoding='utf-8')
            return cls.fromdict(d)
