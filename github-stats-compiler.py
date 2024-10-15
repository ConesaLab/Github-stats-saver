#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:23:05 2024

@author: Fabián Robledo @ conesalab
@version: 0.9

Downloads the insights of a github repo as different csv files

usage: github-stats-compiler.py -k <github_passkey> -u <owner> -r <repository

"""

# Modules needed to connect to the API
import argparse
import datetime
import logging
import json
import os
import urllib.request

# Github API URLs
GITHUB_API_URL:str = "https://api.github.com/repos/{owner}/{repo}/"
GITHUB_RELEASE_API_URL:str = os.path.join(GITHUB_API_URL, "releases")
GITHUB_PATHS_API_URL:str = os.path.join(GITHUB_API_URL, "traffic/popular/paths")
GITHUB_REFERRERS_API_URL:str = os.path.join(GITHUB_API_URL, "traffic/popular/referrers")
GITHUB_CLONES_API_URL:str = os.path.join(GITHUB_API_URL, "traffic/clones")
GITHUB_POPULAR_PATHS:str = os.path.join(GITHUB_API_URL, "traffic/popular/paths")
GITHUB_REFFERAL_SOURCE:str = os.path.join(GITHUB_API_URL, "traffic/popular/referrers")
GITHUB_TRAFFIC_VIEWS:str = os.path.join(GITHUB_API_URL, "traffic/views")

ASSETS: str = "assets"
DOWNLOAD_COUNTS: str = "download_count"
NO_ASSETS_WARNING: str = "No assets attached to release {release}, so Github does not provide download info"
RELEASE_TAG: str = "tag_name"
OWNER: str = "conesalab"
REPO: str = "sqanti3"
CLONES: str = "clones"

def parseargs():
    """
    A parser function using argparse.
    
    Returns
    -------
    TYPE
        The parsed arguments with each argument as an element inside the returned object.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", type=str, help="User owner of the repository in github", default="conesalab")
    parser.add_argument("-r", "--repo", type=str, help="name of repository in github", default="sqanti3")
    parser.add_argument("-c", "--clone_info", type=str, help="Filename to save clone info", default="clone.csv")
    parser.add_argument("-v", "--views_info", type=str, help="Filename to save views info", default="visits.csv")
    parser.add_argument("-d", "--download_info", type=str, help="Filename to save clone info", default="download.csv")
    parser.add_argument("-ref", "--referrals_info", type=str, help="Filename to save clone info", default="referrals.csv")
    parser.add_argument("-p", "--pages_info", type=str, help="Filename to save pages info", default="pages_visit.csv")
    parser.add_argument("-l", "--logfile", type=str, help="Filename to save logging info", default="monitor.log")
    parser.add_argument("-k", "--apikey", type=str, help="Github API key")
    return parser.parse_args()

def main():
    args = parseargs()
    logging.basicConfig(filename=args.logfile, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("="*20+" Starting execution "+"="*20)
    logging.info("Connecting to GITHUB API to get clone info")
    # There are a lot of errors to handle when trying to connect to the API.
    # Mainly we face the problem of unauthorized of forbidden queries to the
    # API. However, there might be other problems that, even unlikely
    # we might face in the future: API changes or redirection of URL, 
    try: 
        clone_info = connect_to_API(GITHUB_CLONES_API_URL, args.apikey, args.user, args.repo)
        logging.info("Clone info retrieved")
        logging.info("Saving clone info into {file}".format(file=args.clone_info))
        save_clone_info(clone_info, args.clone_info)
    except urllib.error.HTTPError as httperror:
        logging.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    
    try:
        logging.info("Connecting to GITHUB API to get download info")
        download_info = get_downloads_of_release(args.user, args.repo)
        logging.info("Download info retrieved")
        try:
            save_download_info(download_info, args.download_info)
        except Exception as e:
            logging.error("Could connect to API but not save the data. Check disk usage or availability")
            print(e)
    except Exception:
        logging.error("Could not get info from: "+GITHUB_API_URL.format(owner=args.user, repo=args.repo))
    
    try: 
        logging.info("Connecting to GITHUB API to get views data")
        views = connect_to_API(GITHUB_TRAFFIC_VIEWS, args.apikey, args.user, args.repo)
        logging.info("Retrieved views data")
        save_views_info(views, args.views_info)
    except urllib.error.HTTPError as httperror:
        logging.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try: 
        logging.info("Connecting to GITHUB API to get popular pages data")
        pages = connect_to_API(GITHUB_POPULAR_PATHS, args.apikey, args.user, args.repo)
        logging.info("Retrieved popular pages data")
        save_pages_info(pages, args.pages_info)
    except urllib.error.HTTPError as httperror:
        logging.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try:
        logging.info("Connecting to GITHUB API to get referrals data")
        referrals = connect_to_API(GITHUB_REFFERAL_SOURCE, args.apikey, args.user, args.repo)
        logging.info("Saving referral info")
        save_referral_info(referrals, args.referrals_info)
    except urllib.error.HTTPError as httperror:
        logging.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))


def connect_to_API(url:str, apikey:str, owner:str, repo:str) -> dict:
    pass_header:str = "Bearer {password}".format(password=apikey)
    authorization_header:str = "Authorization"
    header: dict = {authorization_header: pass_header}
    request = urllib.request.Request(url.format(owner=owner, repo=repo), headers=header)
    request.add_header(authorization_header, pass_header)
    response = urllib.request.urlopen(request)
    return json.loads(response.read())

def save_referral_info(referrals:dict, filename:str) -> int:
    today = datetime.datetime.now()
    data = list(map(lambda x: ",".join([today.strftime("%d/%m/%Y %H:%M:%S"), x["referrer"], str(x["count"]), str(x["uniques"])]),referrals))
    if(not os.path.exists(filename)):
        writer = open(filename, "wt")
        writer.write(",".join(["Date","Referrer","Counts","Uniques"])+"\n")
        writer.close()
    with open(filename, "at") as fwriter:
        [fwriter.write("{row}\n".format(row=row)) for row in data]
    return 0

def save_pages_info(pages:dict, save_path:str) -> int:
    """    

    Parameters
    ----------
    pages : dict
        The dict obtained from github API.
    save_path : str
        The csvfile where data will be saved.

    Returns
    -------
    int
        An int code, where 0 means everything was correct.

    """
    with open(save_path, "at") as fwriter:
        for element in pages:
            data = ",".join([datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), element["path"], element["title"], str(element["count"]), str(element["uniques"])])+"\n"
            fwriter.write(data)
    return 0

def save_views_info(views:dict, save_path: str) -> int:
    """
    

    Parameters
    ----------
    views : dict
        DESCRIPTION.
    save_path : str
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    raw_views = views["views"]
    if(os.path.exists(save_path)):
        data = open(save_path,"rt")
        knowntimestamps = set(map(lambda x: x.split(",")[0], data))
        raw_views = list(filter(lambda x: False if x["timestamp"] in knowntimestamps else True, raw_views))
        data.close()
    else:
        writer = open(save_path, "wt")
        writer.write("Date,count,uniques\n")
        writer.close()
    data_rows = "\n".join(map(lambda x: ",".join([x["timestamp"], str(x["count"]), str(x["uniques"])]), raw_views))
    with open(save_path, "at") as fwriter:
        fwriter.write(data_rows+"\n")
    return 0

def save_clone_info(clone_info:dict, filename: str) -> 0:
    """
    Saves the clone info into a csv file. 

    Parameters
    ----------
    clone_info : dict
        DESCRIPTION.
    filename : str
        DESCRIPTION.

    Returns
    -------
    int: 0 if everything went correct.
    """
    timestamps_obj:list = clone_info[CLONES]
    if(os.path.exists(filename)):
        data = open(filename,"rt")
        knowntimestamps = set(map(lambda x: x.split(",")[0], data))
        timestamps_obj = list(filter(lambda x: False if x["timestamp"] in knowntimestamps else True, timestamps_obj))
        data.close()
    else:
        writer = open(filename, "wt")
        writer.write("Date,clones,uniques\n")
        writer.close()
    data = list(map(lambda x: ",".join([x["timestamp"], str(x["count"]), str(x["uniques"])]) ,timestamps_obj))
    with open(filename, "at") as fwriter: # Opening in append text mode
        [fwriter.write("{row}\n".format(row=x)) for x in data]
    return 0
    
def save_download_info(download_info:dict, filename):
    """
    

    Parameters
    ----------
    download_info : dict
        DESCRIPTION.
    filename : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    today = datetime.datetime.now()
    data = list(map(lambda x: ",".join([today.strftime("%d/%m/%Y %H:%M:%S"), x,str(download_info[x])]),download_info.keys()))
    if(not os.path.exists(filename)):
        writer = open(filename, "wt")
        writer.write(",".join(["Date","Version","Downloads"])+"\n")
        writer.close()
    with open(filename, "at") as fwriter:
        [fwriter.write("{row}\n".format(row=row)) for row in data]

def _parse_downloads_of_release(json_release: dict) -> int:
    """
    Parameters
    ----------
    json_release : dict
        A dictionary with the data to parse from the API. Particularly, a JSON
        dictionary with the data from one GITHUB release, obtained using
        the API URL: https://api.github.com/repos/{owner}/{repo}/releases.

    Returns
    -------
    int
        The number of times an Asset of this release has been download.
        With Sqanti3 we assume that any file is a copy of the source code.
        This number does not include the authomatically generated source
        code that github provides

    """
    total_downloads:int = 0
    if(json_release[ASSETS]): # Check if assets were attached. Element always
    # exists as an array that is empty if no assests where attached
        total_downloads = sum(map(lambda data: int(data[DOWNLOAD_COUNTS]), json_release[ASSETS]))
    else:      
        logging.warning(NO_ASSETS_WARNING.format(release=json_release[RELEASE_TAG]))
    return total_downloads

def get_downloads_of_release(owner:str, repo:str) -> dict:
    """
    Parameters
    ----------
    owner : str
        The user that owns the repository.
    repo : str
        The name of the repository.
    Returns
    -------
    dict
        A dictionary with the key-value pairs corresponding to {version: downloads}.
    """
    with urllib.request.urlopen(GITHUB_RELEASE_API_URL.format(owner=owner, repo=repo)) as response:
        data:str = response.read()
        json_data:dict = json.loads(data)
        assets_counts: dict[str:int] = dict()
        for release in json_data:
            assets_counts[release[RELEASE_TAG]] = _parse_downloads_of_release(release)
    return assets_counts

if __name__ == "__main__":
    main()
