#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:23:05 2024

@author: Fabián Robledo @ conesalab
@version: 0.2.1

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
    parser.add_argument("-l", "--logfile", type=str, help="Filename to save logging info", default="monitor.log")
    parser.add_argument("-c", "--config", type=str, help="Config with the repositories to work with", default=None, required=True)
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug logging info", default=False)
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

def get_stats_for_tool(tool:dict, tool_name:str, folder:str):
    # Logger for the tool
    logger = logging.getLogger(tool_name)
    logger.info("Starting: {}".format(tool_name))

    for repository in tool.keys():
        logger.info("Connecting to {}".format(repository))
        match repository:

            case "github": get_github_stats(tool[repository]["owner"], tool[repository]["repo"], 
                                            tool[repository]["apikey"], os.path.join(folder, tool[repository]["savefile_prefix"]))
                
            case "docker": get_docker_stats(tool[repository]["owner"], tool[repository]["repo"],
                                            tool[repository]["apikey"], os.path.join(folder, tool[repository]["savefile"]))
                
            case "conda":  get_conda_stats(tool[repository]["owner"], 
                                           tool[repository]["repo"],
                                           os.path.join(folder, tool[repository]["savefile"]))
            case "cran":   pass

            case "bioconductor": get_bioconductor_stats(tool[repository]["package"], 
                                                        os.path.join(folder, tool[repository]["savefile"]))
            case _:
                logging.error("Repository not supported: {}".format(repository))
    pass

def main():
    # There are a lot of errors to handle when trying to connect to the API.
    # Mainly we face the problem of unauthorized of forbidden queries to the
    # API. However, there might be other problems that, even unlikely
    # we might face in the future: API changes or redirection of URL, 
    

    # Check logging level from arguments to show debug info or not
    # Debug mode can be activated by using the --debug flag
    # Else only shos info messages
    args = parseargs()
    loglevel = logging.DEBUG if args.debug else logging.INFO 
    logging.basicConfig(filename=args.logfile, level=loglevel, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # One logger per repository to make easy to know where failed
    # GSS (Github stats saver) is the one used for any message not related 
    # to a specific element of the code (repositories, backup, etc)
    logger = logging.getLogger("GSS") 

    logger.info("="*20+" Starting execution "+"="*20)
    logger.debug("Debug mode activated: saving into {}".format(args.logfile))
    logger.info("Loading config file from: {path}".format(path=args.config))

    config = config_reader.load_config(args.config)

    logger.debug("Config file loaded")

    tools_data = config["tools"]

    logger.info("{} tools to monitor".format(len(tools_data)))
    logger.debug("{} tools ".format(tools_data))

    for tool in tools_data.keys():
        get_stats_for_tool(tools_data[tool], tool, config["root_folder"])

    logger.info("Connecting to GITHUB API to get clone info")

    if (config["backup"]["activate"]):
        backup_data = config["backup"]
        logger_backup = logging.getLogger("Backup")
        # We can face several errors when making the backup
        # The most usual will be the network connection error to the webdab server
        # But maybe there are others
        try:
            files:list = [os.path.join(config["root_folder"], file) for file in os.listdir(config["root_folder"]) if file.endswith(".csv")]
            logger_backup.info("Backup of {} files".format(len(files)))
            logger_backup.debug("Files to backup: {}".format(files))
            filename:str = "backup-stats-{}.tar.gz".format(datetime.datetime.today().strftime('%Y-%m-%d'))
            tar_gz_file:str = os.path.join(config["root_folder"], filename)
            logger_backup.debug("Backup file: {}".format(tar_gz_file))
            backup._tar_gz(files, tar_gz_file)
            logger_backup.info("Generated backup file: {}".format(tar_gz_file))
            status = backup._upload(backup_data["backup_url_folder"], tar_gz_file, filename, backup_data["user"], backup_data["password"])
            logger_backup.debug("Status code: {}".format(status))
            if (status == 204):
                logger_backup.info("Backup file uploaded succesfully")
            elif (status == 404):
                logger_backup.error("Remote folder to store the backup is not found: {}".format(backup_data["backup_url_folder"]))
                
        except urllib.error.HTTPError as neterror:
            logger_backup.error("Could not upload backup because of error: {}".format(neterror))
        except Exception as error:
            logger_backup.error("Unhandled error: {}".format(error))
            logger_backup.error("Backup not completed.")

if __name__ == "__main__":
    main()
