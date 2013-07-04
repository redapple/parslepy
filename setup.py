#!/usr/bin/env python

from distutils.core import setup

setup(name='parslepy',
      version='0.1.1',
      description='Parsley extraction library using lxml',
      long_description="""
========
Parslepy
========

Parslepy lets you extract content from HTML and XML documents
where extraction rules are defined using a JSON object
or equivalent Python dict,
where keys are names you want to assign to extracted content,
and values are CSS selectors or XPath expressions.

Parslepy is an implementation of the Parsley extraction
language defined `here <https://github.com/fizx/parsley>`_,
using lxml and cssselect.

You can nest objects, generate list of objects, and (to
a certain extent) mix CSS and XPath.

Parslepy uderstands what lxml and cssselect understand,
which is roughly CSS3 selectors and XPath 1.0 expressions.

Documentation & examples
========================

See https://github.com/redapple/parslepy/wiki#usage
      """,
      author='Paul Tremberth',
      author_email='paul.tremberth@gmail.com',
      packages=['parslepy'],
      requires=['lxml', 'cssselect'],
      install_requires=[
        "lxml >= 3.0",
        "cssselect",
      ],
      classifiers = [
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
     ],
     url = 'https://github.com/redapple/parslepy',
)
