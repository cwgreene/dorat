#/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import json

import requests
import zipfile

from tempfile import TemporaryDirectory

import re
CONFIG_DIR = os.path.expanduser("~/.config/github.com/cwgreene/dorat/")
CONFIG_FILE = os.path.expanduser(CONFIG_DIR + "/dorat.json")

GHIDRA_ZIP_FILE="ghidra_10.1.1_PUBLIC_20211221.zip"
GHIDRA_VERSION="ghidra_10.1.1_PUBLIC"

MARK_PREFIX = "^(INFO |ERROR) {}> (.*)"
MARK_END = " (GhidraScript)  \n"

def parse_output(proc, options):
    state = "SCAN"
    mark_prefix = MARK_PREFIX.format(options.script)
    for line in iter(proc.stdout.readline, b''):
        line = str(line, 'utf8')
        if options.show_raw:
            sys.stdout.write(line)
        elif state == "SCAN":
            m = re.match(mark_prefix, line)
            if m:
                line = m.group(2) + "\n"
                if not line.endswith(MARK_END):
                    sys.stdout.write(line)
                    state = "DUMP"
                else:
                    line = line.replace(MARK_END, "\n")
                    sys.stdout.write(line)
            #else: skip
        elif state == "DUMP":
            if line.endswith(MARK_END):
                line = line.replace(MARK_END, "\n")
                sys.stdout.write(line)
                state = "SCAN"
            else:
                sys.stdout.write(line)

    if options.show_stderr:
        sys.stdout.write(str(proc.stderr.read(), 'utf8'))

def resolve_config():
    if not os.path.exists(CONFIG_FILE):
        print("Configuration json file not found in {}.".format(CONFIG_FILE))
        print("Please run --config to configure your ghidra application and scripts directory")
        sys.exit(1)
    with open(CONFIG_FILE) as config_file:
        return json.load(config_file)

def write_config_file(path_ghidra, path_scripts, java_home):
    with open(CONFIG_FILE, "w") as json_file:
        json.dump( {
            "version": "1",
            "GHIDRA_INSTALL_DIR":path_ghidra,
            "GHIDRA_SCRIPTS_DIR":path_scripts,
            "JAVA_HOME": java_home
        }, json_file)

def configure_dorat():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    print("Path to Ghidra Root Directory: ", end="")
    path_ghidra = input()
    path_ghidra = os.path.expanduser(path_ghidra)
    print("Path to Ghidra Scripts Directory: ", end="")
    path_scripts = input()
    path_scripts = os.path.expanduser(path_scripts)
    print("Path to Java bin directory: ", end="")
    java_home = input()
    java_home = os.path.expanduser(java_home)
    write_config_file(path_ghidra, path_scripts, java_home)
def is_dorat_configured():
    if not os.path.exists(CONFIG_FILE):
        return False
    with open(CONFIG_FILE) as config_file:
        data = config_file.read()
        js = json.load(data)
        if "GHIDRA_INSTALL_DIR" in js and "GHIDRA_SCRIPTS_DIR" in js:
            return True
    return False

def download_ghidra(options):
    print("Downloading Ghidra")
    with requests.get("https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.1.1_build/ghidra_10.1.1_PUBLIC_20211221.zip", stream=True) as r:
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
    return subprocess.run(["/bin/sh", "./install.sh", 
        f"{options.ghidra_install_dir}/{GHIDRA_VERSION}"],
        cwd=f"{options.ghidra_scripts_install_dir}")

def install_ghidrascripts(options):
    clone_ghidrascripts(options)
    run_ghidrascripts_install(options)

def install_ghidra(options):
    if options.force == False and is_dorat_configured():
        print("Ghidra is installed and dorat is configured")
        return
    download_ghidra(options)
    install_ghidrascripts(options)
    write_config_file(
        f"{options.ghidra_install_dir}/{GHIDRA_VERSION}",
        options.ghidra_scripts_install_dir)

def main():
    parser = argparse.ArgumentParser()
    main_group = parser.add_argument_group(title="main group")
    main_group.add_argument("--binary", help="REQUIRED: target binary")
    main_group.add_argument("--script", help="REQUIRED: target script")
    main_group.add_argument("--show-stderr", action="store_true", help="dump stderr")
    main_group.add_argument("--show-raw", action="store_true", help="dump raw output")
    list_group = parser.add_argument_group(title="list command")
    list_group.add_argument("--list", action="store_true", help="list scripts")
    config_group = parser.add_argument_group(title="configuration options")
    config_group.add_argument("--config", action="store_true", help="configure dorat")
    config_group.add_argument("--config-info", action="store_true", help="show dorat configuration in {}".format(CONFIG_FILE))
    install_group = parser.add_argument_group("title=install ghidra")
    install_group.add_argument("--install-ghidra", action="store_true")
    install_group.add_argument("--ghidra-install-dir")
    install_group.add_argument("--ghidra-scripts-install-dir")
    install_group.add_argument("--force", action="store_true", default=False)
    options, args = parser.parse_known_args()

    if options.config_info:
        with open(CONFIG_FILE) as configfile:
            print(configfile.read())
        sys.exit(0)

    if options.config:
        configure_dorat()
        print("Dorat is configured. Enjoy!")
        sys.exit(0)

    if options.install_ghidra:
        if not options.ghidra_install_dir:
            raise(Exception("Need --ghidra-install-dir"))
        if not options.ghidra_scripts_install_dir:
            raise(Exception("Need --ghidra-scripts-install-dir"))
        if os.path.exists(options.ghidra_scripts_install_dir):
            raise(Exception(f"{options.ghidra_scripts_install_dir} already exists"))
        options.ghidra_install_dir = os.path.expanduser(
                options.ghidra_install_dir)
        options.ghidra_scripts_install_dir = os.path.expanduser(
                options.ghidra_scripts_install_dir)
        install_ghidra(options)
        sys.exit(0)
    config = resolve_config()

    if options.list:
        # TODO: do all of the standard locations
        for afile in os.listdir(config["GHIDRA_SCRIPTS_DIR"]):
            if afile.endswith(".java"):
                print(afile)
        return

    if not options.binary or not options.script:
        parser.print_help()
        print("--binary and --script are required when not used with list")
        return

    # Ensure that expected version of java is used
    path = config["JAVA_HOME"] + ":" + os.environ["PATH"]
    envvars = os.environ.copy()
    envvars["PATH"] = path

    proc  = subprocess.Popen(["{}/support/analyzeHeadless".format(config["GHIDRA_INSTALL_DIR"]),
            '/tmp/', 'ProjectName',
            '-import', options.binary,
            '-deleteProject',
            # TODO: make this part of a analysis/script group.
            '-preScript', 'ResolveX86orX64LinuxSyscallsScript.java',
            '-scriptPath', config["GHIDRA_SCRIPTS_DIR"],
            '-postScript', options.script,
            ]+args,
            env=envvars,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    parse_output(proc, options)

if __name__ == "__main__":
    main()
