#!/usr/bin/env python

from distutils.core import setup

setup(name='andrey',
      version='0.1.0',
      description='A markov chain library',
      author='Eric Stein',
      url='https://github.com/eastein/andrey',
      packages=['andrey'],
      install_requires=['msgpack-python']
      )
