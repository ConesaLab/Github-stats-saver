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
    request = urllib.request.Request(API_url.format(owner=owner, repo=repo))
    response = urllib.request.urlopen(request)
    json_data =  json.loads(response.read())
    downloads = ((version["version"], version["ndownloads"]) for version in json_data["files"])
    return downloads

def save_conda_stats(conda_stats:tuple, conda_file):
    data = "\n".join(map(lambda x: ",".join(x)))
    print(data)