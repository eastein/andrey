#!/usr/bin/env python

from distutils.core import setup

setup(name='andrey',
      version='0.0',
      description='A markov chain lib and IRC bot',
      author='Eric Stein',
      url='https://github.com/eastein/andrey',
      packages=['andrey'],
      install_requires=['msgpack-python']
      )
