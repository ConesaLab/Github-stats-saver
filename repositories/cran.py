#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 11:17:49 2024

@author: frobledo
"""

import logging
import urllib.request

# Note that cranlogs only shows downloads since RStudio started tracking them in 2012
BASE_URL: str = "https://cranlogs.r-pkg.org/badges/grand-total/{package}"
logger = logging.getLogger("Bioconductor")

def downloads_in_cran(package):
    url:str = BASE_URL.format(package=package)
    with urllib.request.urlopen(url) as response:
        error_code:int = response.getcode()
        logging.info("Connecting to cranlogs...")
        if (error_code == 200):
            logging.info("Succesfully connected to fetch cran downloads for: {package}".format(package=package))
            data = response.read()
        else:
            logging.error("Error connecting to cranlogs to fetch downloads for: {package}".format(package=package))