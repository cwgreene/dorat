#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='dorat',
      version='1.0',
      description='',
      author='cwgreene',
      author_email='archgoon+dorat@gmail.com',
      url='',
      install_requires=["requests"],
      packages=find_packages(),
      scripts=["bin/dorat"]
     )
