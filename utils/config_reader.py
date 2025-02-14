#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 11:32:26 2024

@author: frobledo
"""

import os
import json
import logging


logger = logging.getLogger("Config reader")

def _create_dir_if_not_exists(folder:str):
    """
        Creates directory folder if not exists
        Else does nothing
    """
    if not os.path.exists(folder):
        logging.info("Directory {folder} does not exist. Creating it".format(folder=folder))
        os.makedirs(folder)
    else:
        logging.info("Directory {folder} already exists".format(folder=folder))

def check_all_directories(config:dict):
    """
        Checks if all directories in config exist
        If not, creates them
    """
    logging.info("Checking if all directories in config exist")
    tools = config["tools"]
    for repository in tools:
        for website in tools["repository"]:
            pass



def load_config(path:str) -> dict:
    path:str = os.path.abspath(path)
    logging.info("Loading config file from: {path}".format(path=path))
    config:dict = json.load(open(path))
    logging.info("Config file loaded succesfully")
    return config