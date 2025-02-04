#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:37:21 2024

@author: frobledo
"""

import datetime

import os
import json
import logging
import urllib

CONDA_API:str = "https://api.anaconda.org/package/{owner}/{repo}"
logger = logging.getLogger("Conda")

def get_conda_stats(API_url:str, owner:str, repo:str) -> list:
    url:str = API_url.format(owner=owner, repo=repo)
    logging.info("Connecting to {}".format(url))
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    json_data =  json.loads(response.read())
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info("Date recieved: {date}".format(date=date))
    ## For every version (represented by every row) we have date, version and absolute number of downloads
    data = [(date, version["version"], str(version["ndownloads"])) for version in json_data["files"]]
    downloads = [",".join(row) for row in data]
    text = "\n".join(downloads)
    return text

def save_conda_stats(conda_stats:tuple, conda_file:str) -> None: 
    print(conda_stats)
    if (not os.path.exists(conda_file)):
        logger.info("File {conda_file} does not exist. Creating with headers".format(conda_file=conda_file))
        headers = "Date,Version,Downloads"
    print(conda_stats, end="", file=open(conda_file, "at"))