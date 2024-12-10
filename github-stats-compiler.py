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
import backup
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
    parser.add_argument("-u", "--user", type=str, help="User owner of the repository in github", required=True)
    parser.add_argument("-r", "--repo", type=str, help="name of repository in github", required=True)
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
    return parser.parse_args()

def main():
    args = parseargs()    
    logger = logging.getLogger("Github") # One logger per repository to make easy to know what failed
    logging.basicConfig(filename=args.logfile, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("="*20+" Starting execution "+"="*20)
    logger.info("Connecting to GITHUB API to get clone info")
    # There are a lot of errors to handle when trying to connect to the API.
    # Mainly we face the problem of unauthorized of forbidden queries to the
    # API. However, there might be other problems that, even unlikely
    # we might face in the future: API changes or redirection of URL, 
    try: 
        clone_info = github.connect_to_API(github.GITHUB_CLONES_API_URL, args.apikey, args.user, args.repo)
        logger.info("Clone info retrieved")
        logger.info("Saving clone info into {file}".format(file=args.clone_info))
        github.save_clone_info(clone_info, args.clone_info)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    
    try:
        logger.info("Connecting to GITHUB API to get download info")
        download_info = github.get_downloads_of_release(args.user, args.repo)
        logger.info("Download info retrieved")
        try:
            github.save_download_info(download_info, args.download_info)
        except Exception as e:
            logger.error("Could connect to API but not save the data. Check disk usage or availability")
            print(e)
    except Exception:
        logger.error("Could not get info from: "+github.GITHUB_API_URL.format(owner=args.user, repo=args.repo))
    
    try: 
        logger.info("Connecting to GITHUB API to get views data")
        views = github.connect_to_API(github.GITHUB_TRAFFIC_VIEWS, args.apikey, args.user, args.repo)
        logger.info("Retrieved views data")
        github.save_views_info(views, args.views_info)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try: 
        logger.info("Connecting to GITHUB API to get popular pages data")
        pages = github.connect_to_API(github.GITHUB_POPULAR_PATHS, args.apikey, args.user, args.repo)
        logger.info("Retrieved popular pages data")
        github.save_pages_info(pages, args.pages_info)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try:
        logger.info("Connecting to GITHUB API to get referrals data")
        referrals = github.connect_to_API(github.GITHUB_REFFERAL_SOURCE, args.apikey, args.user, args.repo)
        logger.info("Saving referral info")
        github.save_referral_info(referrals, args.referrals_info)
    except urllib.error.HTTPError as httperror:
        logger.error("Could not connect to GITHUB API due to the error: {error}. If its 401 Unauthorized or 403 Forbidden, please check that the api key has push permission".format(error=httperror))
    try:
        if (args.docker_user is None or args.docker_repo is None):
            logging.getLogger("Docker")
            logging.info("No Docker credentials provided: docker user or repository given")
        else:
            docker_stats = docker.get_docker_stats(docker.REPOSITORY_API_URL, args.docker_user, args.docker_repo)
            docker.save_docker_stats(docker_stats[0], docker_stats[1], args.docker)
    except urllib.error.HTTPError as httperror:
        logger_docker = logging.getLogger("Docker")
        logger_docker.error("Error connecting to Dockerhub: {error}".format(error=httperror))
    try:
        conda_stats = conda.get_conda_stats(conda.CONDA_API, args.user, args.repo)
        conda.save_conda_stats(conda_stats[0], conda_stats[1], args.conda)
    except urllib.error.HTTPError as httperror:
        logger_conda = logging.getLogger("Conda")
        logger_conda.error("Error connecting to Conda: {error}".format(error=httperror))

    if (args.backup is not None):
        
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
