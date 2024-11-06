#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:09:14 2024

@author: frobledo
"""

import os
import datetime
import json
import logging
import urllib

REPOSITORY_API_URL:str = "https://hub.docker.com/v2/repositories/{owner}/{repository}"
logger = logging.getLogger("Docker")

def connect_to_docker_API(url:str, owner:str, repo:str) -> dict:
    request = urllib.request.Request(url.format(owner=owner, repository=repo))
    response = urllib.request.urlopen(request)
    return json.loads(response.read())

def get_docker_stats(API:str, owner:str, repo:str) -> (int,int):
    data:dict = connect_to_docker_API(API, owner, repo)
    pulls:int = data["pull_count"]
    stars:int = data["star_count"]
    logger.info("Pulls: {pulls}".format(pulls=pulls))
    logger.info("Stars: {stars}".format(stars=stars))
    return pulls, stars

def save_docker_stats(pulls:int, stars:int, filename:str):
    today = datetime.datetime.today()
    if (not os.path.exists(filename)): # Making sure the header is written
        with open(filename, "wt") as fwriter:
            fwriter.write("Date,pulls,stars\n")
    with open(filename, "at") as fwriter:
        fwriter.write(",".join([today.strftime("%d/%m/%Y %H:%M:%S"), str(pulls), str(stars)])+"\n")