#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import sys

from andrey import persist

if __name__ == '__main__':
    f, t = (2, 3)
    try:
        f, t = (int(sys.argv[2]), int(sys.argv[3]))
    except IndexError:
        pass

    fn = sys.argv[1]

    print('%s %d %d' % (fn, f, t))

    m = persist.PersistedMarkov.restore(fn, f, t)

    for line in sys.stdin:
        line = line.strip()
        m.teach(line)

    m.save(fn)
