#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 11:32:26 2024

@author: frobledo
"""

import os
import json
import logging

import collections

logger = logging.getLogger("Config reader")

def load_config(path:str) -> dict:
    path:str = os.path.abspath(path)
    logging.info("Loading config file from: {path}".format(path=path))
    config:dict = json.load(open(path))
    logging.info("Config file loaded succesfully")
    return config