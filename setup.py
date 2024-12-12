#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 10:19:44 2024

@author: frobledo
"""

from setuptools import setup

setup(
   name='Github-stats-saver',
   version='0.1.0',
   description='Recovers stats of a package for several repositories',
   author='Fabián Robledo',
   author_email='fabian.robledo@csic.es',  
   install_requires=['requests==2.32.3'], #external packages as dependencies
   scripts=["github-stats-compiler.py"],
   packages=["repositories", "utils"]
)