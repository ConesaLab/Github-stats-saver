#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import sys

ROOT:str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
print(ROOT)

import unittest
import repositories.bioconductor as BioC

class test_bioconductor(unittest.TestCase):

    def test_url(self):
        pass

if __name__=="__main__":
    unittest.main()