#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:37:21 2024

@author: frobledo
"""

import json
import logging
import urllib

CONDA_API:str = "https://api.anaconda.org/package/{owner}/{repo}"
logger = logging.getLogger("Conda")

def get_conda_stats(API_url:str, owner:str, repo:str) -> ():
    url:str = API_url.format(owner=owner, repo=repo)
    logging.info("Connecting to {}".format(url))
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    json_data =  json.loads(response.read())
    downloads = [",".join([version["version"], str(version["ndownloads"])]) for version in json_data["files"]]
    return downloads

def save_conda_stats(conda_stats:tuple, conda_file):
    # There's something i have yet to find in list comprehension, but for now I take the first element because the list is inside another list it shouldn't be
    data = "\n".join(conda_stats[0]) 
    print(data, file=open(conda_file, "at"))