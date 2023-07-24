import os
import json
import requests
import re
import sys

import zipfile

from tempfile import TemporaryDirectory

GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.3.2_build/ghidra_10.3.2_PUBLIC_20230711.zip"
GHIDRA_ZIP_FILE=GHIDRA_URL.split("/")[-1] # ghidra_10.3.2_PUBLIC_20230711.zip
GHIDRA_VERSION=GHIDRA_URL.split("/")[-1].rsplit("_",1)[0] # "ghidra_10.3.2_PUBLIC"

def download_ghidra(options):
    print("Downloading Ghidra")
    with requests.get(f"https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.3.2_build/ghidra_10.3.2_PUBLIC_20230711.zip", stream=True) as r:
        r.raise_for_status()
        with TemporaryDirectory() as tmpdir:
            zipfilepath = f"{tmpdir}/{GHIDRA_ZIP_FILE}.zip"
            with open(zipfilepath, 'wb') as tmpzip:
                for chunk in r.iter_content(chunk_size=8192*1024):
                    tmpzip.write(chunk)
            print("Downloaded Ghidra, unzipping")
            with zipfile.ZipFile(zipfilepath) as zf:
                zf.extractall(options.ghidra_install_dir)
            print(f"Unzipped Ghidra into {options.ghidra_install_dir}")
def clone_ghidrascripts(options):
    import subprocess
    return subprocess.run(["git", "clone",
            "https://github.com/cwgreene/ghidrascripts",
            options.ghidra_scripts_install_dir])
def run_ghidrascripts_install(options):
    import subprocess
    result =  subprocess.run(["/bin/sh", "./install.sh", 
        f"{options.ghidra_install_dir}/{GHIDRA_VERSION}"],
        cwd=f"{options.ghidra_scripts_install_dir}")
    if result.returncode != 0:
        raise Exception("Failed to run git clone")

def install_ghidrascripts(options):
    clone_ghidrascripts(options)
    run_ghidrascripts_install(options)

def install_ghidra(options):
    if options.force == False and is_dorat_configured():
        print("Ghidra is installed and dorat is configured")
        return
    download_ghidra(options)
    install_ghidrascripts(options)

def find_ghidra_installs(start_dir):
    results = []
    matcher = MatchAction(r"ghidra_[0-9]*\.[0-9]*\.[0-9]*_PUBLIC", lambda p: [])
    for ghidra_install in dirwalk(stard_dir, action=matcher):
        pass
    return []


