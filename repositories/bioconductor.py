#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 11:17:35 2024

@author: frobledo
"""

import os
import platform
import datetime
import logging
import urllib.request

###########################
# MacOS user alert        #
###########################
#
# According to the docs, using the urllib.request module is unsafe in combination with os.fork() in MacOS
# https://docs.python.org/3/library/urllib.request.html
# The solution is to set an environment variable "no_proxy" to the value "*"
# There are no fork calls in this package (at the time of writing) and are not expected to
# be implemente. However, just in case someone wants to do some unexpected shenanigans with this
# script and os.fork, the patch will be applied here.
if platform.system() == "Darwin":
    os.environ["no_proxy"] = "*"

BASE_URL:str = "https://www.bioconductor.org/packages/stats/bioc/{package}/{package}_stats.tab"
DOWNLOAD_START:str = "Download started for Bioconductor info for package {package}"
logger = logging.getLogger("Bioconductor")

def download_table(package:str, save_path:str, overwrite:bool=False) -> list[bool]:
    """
    Parameters
    ----------
    package : str
        The name of the package to download stats.
    save_path : str
        Path to save the donwloaded info
    overwrite : bool
        Whether to overwrite or not the info of a year already downloaded
        True: overwrite
        False: Keep old
    

    Returns
    -------
    list[bool]
        A list with length equal to the number of years, which hold booleans:
            A boolean in position x indicates year in position x has been downloaded
            (True) or not (False).

    """
    logging.info(DOWNLOAD_START)
    logging.info()
    url:str = BASE_URL.format(package=package)
    #Connect to URL and retrieve the content using urllib
    content:str = ""
    with urllib.request.urlopen(url) as response:
        logging.info("Connected to {url}: code {}".format(url, error_code))
        error_code:int = response.status
        with open(save_path, "wt") as fwrite:
            fwrite.write(response.read())
        logging.info("Save bioconductor download_info") 
    pass

