#!/usr/bin/env python

from distutils.core import setup

setup(name='house',
      version='1.0',
      description='Home automation REST service library',
      author='Bob Helander',
      author_email='email@python.net',
      url='https://github.com/bobhelander/house',
      packages=['house', 
                'house.alarm',
                'house.environment',
                'house.services',
                'house.irrigation',
                'house.data',
                'house.utils'],
     )