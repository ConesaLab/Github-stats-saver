#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 12:08:47 2024

@author: frobledo
"""

import tarfile

import requests
from requests.auth import HTTPBasicAuth

def _tar_gz(files: list, filename: str) -> None:
    """
    
    Compresses all csv into a .tar.gz file to backup them

    Parameters
    ----------
    files : list
        A list containing all files to compress.
    filename : str
        A path, where the tarfile will be saved.

    Returns
    -------
    None
        DESCRIPTION.

    """
    with tarfile.open(filename, "w:gz") as tar:
        for file in files:
            tar.add(file)
    

def _upload(url: str, tarfile: str, remote_name:str, user:str, password:str):
    files = open(tarfile, 'rb')
    req = requests.put("{}/{}".format(url, remote_name), data=files, auth = HTTPBasicAuth(user, password))
    return req.status_code
    