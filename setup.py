#!/usr/bin/env python

from distutils.core import setup

setup(name='parslepy',
      version='0.1',
      description='Parsley extraction library using lxml',
      author='Paul Tremberth',
      author_email='paul.tremberth@gmail.com',
      packages=['parslepy'],
      requires=['lxml'],
     )
