#!/usr/bin/env python

from distutils.core import setup

setup(name='andrey',
      version='0.1.0',
      description='Andrey - Markov Chain library',
      author='Eric Stein',
      author_email='toba@des.truct.org',
      url='https://github.com/eastein/andrey/',
      packages=['andrey'],
      install_requires=['msgpack-python', 'six']
     )
