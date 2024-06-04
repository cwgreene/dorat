import os
import json
import requests
import re
import sys

import zipfile

from .shared import is_dorat_configured

from tempfile import TemporaryDirectory

GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.3.2_build/ghidra_10.3.2_PUBLIC_20230711.zip"
GHIDRA_ZIP_FILE=GHIDRA_URL.split("/")[-1] # ghidra_10.3.2_PUBLIC_20230711.zip
GHIDRA_VERSION=GHIDRA_URL.split("/")[-1].rsplit("_",1)[0] # "ghidra_10.3.2_PUBLIC"

from collections import namedtuple
GhidraOptions = namedtuple("GhidraOptions", ["force", "ghidra_install_dir", "ghidra_scripts_install_dir"])

def download_ghidra(options : GhidraOptions):
    print("Downloading Ghidra")
    with requests.get(f"{GHIDRA_URL}", stream=True) as r:
        r.raise_for_status()
        with TemporaryDirectory() as tmpdir:
            zipfilepath = f"{tmpdir}/{GHIDRA_ZIP_FILE}"
            with open(zipfilepath, 'wb') as tmpzip:
                for chunk in r.iter_content(chunk_size=8192*1024):
                    tmpzip.write(chunk)
            print("Downloaded Ghidra, unzipping")
            import subprocess
            result = subprocess.run(["unzip", zipfilepath, "-d", options.ghidra_install_dir])
            if result.returncode != 0:
                raise("Failed to unzip ghidra zipfile")
            print(f"Unzipped Ghidra into {options.ghidra_install_dir}")

def clone_ghidrascripts(options : GhidraOptions):
    import subprocess
    subprocess.run(["git", "clone",
            "https://github.com/cwgreene/ghidrascripts",
            options.ghidra_scripts_install_dir])
    # Currently we're compatible with 'ac90be33be86e6811741c528c4f4fa55eefb1139'    
    # TODO: Move cloning this out of dorat. Dorat should be target agnostic
    # we should only clone a specific set of scripts for testing purposes.
    return subprocess.run(["git", "-C", options.ghidra_scripts_install_dir, "checkout", "ac90be33be86e6811741c528c4f4fa55eefb1139"])

def run_ghidrascripts_install(options : GhidraOptions):
    import subprocess
    result =  subprocess.run(["/bin/sh", "./install.sh", 
        f"{options.ghidra_install_dir}/{GHIDRA_VERSION}"],
        cwd=f"{options.ghidra_scripts_install_dir}")
    if result.returncode != 0:
        raise Exception("Failed to run git clone")

def install_ghidrascripts(options : GhidraOptions):
    clone_ghidrascripts(options)
    run_ghidrascripts_install(options)

def install_ghidra(options : GhidraOptions):
    if options.force == False and is_dorat_configured():
        print("Ghidra is installed and dorat is configured")
        return
    download_ghidra(options)
    install_ghidrascripts(options)
