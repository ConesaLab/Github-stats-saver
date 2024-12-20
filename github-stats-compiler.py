#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:23:05 2024

@author: Fabián Robledo @ conesalab
@version: 0.9

Downloads the insights of a github repo as different csv files

usage: github-stats-compiler.py -k <github_passkey> -u <owner> -r <repository

"""

# Modules needed to connect to the API, parse the info and log the data
import argparse
import datetime
import logging
import os
import urllib.request

# Modules to connect to the services (including backup)
from utils import backup, config_reader
from repositories import docker, github, conda

def parseargs():
    """
    A parser function using argparse.
    
    Returns
    -------
    TYPE
        The parsed arguments with each argument as an element inside the returned object.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", type=str, help="User owner of the repository in github")
    parser.add_argument("-r", "--repo", type=str, help="name of repository in github")
    parser.add_argument("-c", "--clone_info", type=str, help="Filename to save clone info", default="clone.csv")
    parser.add_argument("-v", "--views_info", type=str, help="Filename to save views info", default="visits.csv")
    parser.add_argument("-d", "--download_info", type=str, help="Filename to save clone info", default="download.csv")
    parser.add_argument("-docker", "--docker", type=str, help="Filename to save docker info", default="docker_stats.csv")
    parser.add_argument("-du", "--docker_user", type=str, help="Username of Dockerhub", default=None)
    parser.add_argument("-dr", "--docker_repo", type=str, help="Repo name in dockerhub", default=None)
    parser.add_argument("-conda", "--conda", type=str, help="Filename to save conda info", default="conda_stats.csv")
    parser.add_argument("-ref", "--referrals_info", type=str, help="Filename to save clone info", default="referrals.csv")
    parser.add_argument("-p", "--pages_info", type=str, help="Filename to save pages info", default="pages_visit.csv")
    parser.add_argument("-l", "--logfile", type=str, help="Filename to save logging info", default="monitor.log")
    parser.add_argument("-k", "--apikey", type=str, help="Github API key")
    parser.add_argument("-b", "--backup", type=str, help="Webdav url to save the backup", default=None)
    parser.add_argument("-bu", "--backup_user", type=str, help="Webdav user to save the backup", default=None)
    parser.add_argument("-bp", "--backup_password", type=str, help="Webdav password to the backup", default=None)
    parser.add_argument("-cg", "--config", type=str, help="Config with the repositories to work with", default=None)
    return parser.parse_args()

def get_github_stats(user:str, repo:str, apikey:str, save_prefix:str):
    logger = logging.getLogger("github")
    try: 
        # Connect to the api, get the info and write it into a csv file
        # An HTTPError is raised if could not connect.
        # TODO: Show the exact error code in the log
        clone_info = github.connect_to_API(github.GITHUB_CLONES_API_URL, apikey, user, repo)
        logger.info("Clone info retrieved")
        clone_file:str = save_prefix+"_clone.csv"
        logger.info("Saving clone info into {file}".format(file=clone_file))
        github.save_clone_info(clone_info, clone_file)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try:
        logger.info("Connecting to GITHUB API to get download info")
        download_info = github.get_downloads_of_release(user, repo)
        download_file:str = save_prefix+"_downloads.csv"
        logger.info("Download info retrieved")
        try:
            github.save_download_info(download_info, download_file)
        except Exception as e:
            logger.error("Could connect to API but not save the data. Check disk usage or availability")
            print(e)
    except Exception:
        logger.error("Could not get info from: "+github.GITHUB_API_URL.format(owner=user, repo=repo))
    
    try: 
        logger.info("Connecting to GITHUB API to get views data")
        views = github.connect_to_API(github.GITHUB_TRAFFIC_VIEWS, apikey, user, repo)
        views_file:str = save_prefix+"_views.csv"
        logger.info("Retrieved views data")
        github.save_views_info(views, views_file)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try: 
        logger.info("Connecting to GITHUB API to get popular pages data")
        pages_file:str = save_prefix+"_pages.csv"
        pages = github.connect_to_API(github.GITHUB_POPULAR_PATHS, apikey, user, repo)
        logger.info("Retrieved popular pages data")
        github.save_pages_info(pages, pages_file)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try:
        logger.info("Connecting to GITHUB API to get referrals data")
        referrals = github.connect_to_API(github.GITHUB_REFFERAL_SOURCE, apikey, user, repo)
        referrals_file:str = save_prefix+"_referrals.csv"
        logger.info("Saving referral info")
        github.save_referral_info(referrals, referrals_file)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    pass

def get_docker_stats(user:str, repo:str, apikey:str, save_file:str):
    logging.getLogger("Docker")
    try:
        docker_stats = docker.get_docker_stats(apikey, user, repo)
        docker.save_docker_stats(docker_stats[0], docker_stats[1], save_file)
    except urllib.error.HTTPError as httperror:
        logger_docker = logging.getLogger("Docker")
        logger_docker.error("Error connecting to Dockerhub: {error}".format(error=httperror))

def get_bioconductor_stats(package:str, savefile:str):
    pass

def get_conda_stats(owner:str, repo:str, savefile:str):
    logger_conda = logging.getLogger("Conda")
    try:
        conda_stats = conda.get_conda_stats(conda.CONDA_API, owner, repo)
        conda.save_conda_stats([conda_stats], savefile)
    except urllib.error.HTTPError as httperror:
        logger_conda.error("Error connecting to Conda API: {error}".format(error=httperror))

    pass

def get_stats_for_tool(tool:dict, tool_name:str):
    logger = logging.getLogger(tool_name)
    logger.info("Starting: {}".format(tool_name))
    for repository in tool.keys():
        logger.info("Connecting to {}".format(repository))
        match repository:

            case "github": get_github_stats(tool[repository]["owner"], tool[repository]["repo"], 
                                            tool[repository]["apikey"], tool[repository]["savefile_prefix"])
                
            case "docker": get_docker_stats(tool[repository]["owner"], tool[repository]["repo"],
                                            tool[repository]["apikey"], tool[repository]["savefile"])
                
            case "conda":  get_conda_stats(tool[repository]["owner"], 
                                           tool[repository]["repo"],
                                           tool[repository]["savefile"])
            case "cran":   pass

            case "bioconductor": get_bioconductor_stats(tool[repository]["package"], 
                                                        tool[repository]["savefile"])
            case _:
                logging.error("Repository not supported: {}".format(repository))
    pass

def main():
    args = parseargs()
    config = config_reader.load_config(args.config)
    logging.basicConfig(filename=args.logfile, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("GSS") # One logger per repository to make easy to know what failed
    tools_data = config["tools"]
    logger.info("="*20+" Starting execution "+"="*20)
    for tool in tools_data.keys():
        get_stats_for_tool(tools_data[tool], tool)
    logger.info("Connecting to GITHUB API to get clone info")
    # There are a lot of errors to handle when trying to connect to the API.
    # Mainly we face the problem of unauthorized of forbidden queries to the
    # API. However, there might be other problems that, even unlikely
    # we might face in the future: API changes or redirection of URL, 
    
    if (args.backup is not None):
        backup_data = config["backup"]
        logger_backup = logging.getLogger("Backup")
        try:
            files:list = [args.clone_info, args.views_info, args.download_info, args.pages_info, args.docker, args.conda, args.referrals_info]
            files:list = list(filter(os.path.exists, files))
            logger_backup.info("Backup of {} files".format(len(files)))
            tar_gz_file:str = "backup-stats-{}.tar.gz".format(datetime.datetime.today().strftime('%Y-%m-%d'))
            backup._tar_gz(files, tar_gz_file)
            logger_backup.info("Generated backup file: {}".format(tar_gz_file))
            backup._upload(args.backup, tar_gz_file, tar_gz_file, args.backup_user, args.backup_password)
            logger_backup.info("Backup file uploaded succesfully")
        except urllib.error.HTTPError as neterror:
            logger_backup.error("Could not upload backup because of error: {}".format(neterror))

if __name__ == "__main__":
    main()
