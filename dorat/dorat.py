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

from . import config

CONFIG_DIR = os.path.expanduser("~/.config/github.com/cwgreene/dorat/")
CONFIG_FILE = os.path.expanduser(CONFIG_DIR + "/dorat.json")

GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.3.2_build/ghidra_10.3.2_PUBLIC_20230711.zip"
GHIDRA_ZIP_FILE=GHIDRA_URL.split("/")[-1] # ghidra_10.3.2_PUBLIC_20230711.zip
GHIDRA_VERSION=GHIDRA_URL.split("/")[-1].rsplit("_",1)[0] # "ghidra_10.3.2_PUBLIC"

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
        config.configure_dorat()
        print("Dorat is configured. Enjoy!")
        sys.exit(0)

    if options.install_ghidra:
        if not options.ghidra_install_dir:
            raise(Exception("Need --ghidra-install-dir"))
        if not options.ghidra_scripts_install_dir:
            raise(Exception("Need --ghidra-scripts-install-dir"))
        if os.path.exists(options.ghidra_scripts_install_dir + "/ghidrascripts") and not options.force:
            raise(Exception(f"{options.ghidra_scripts_install_dir} already exists"))
        options.ghidra_install_dir = os.path.realpath(os.path.expanduser(
                options.ghidra_install_dir))
        options.ghidra_scripts_install_dir = os.path.realpath(os.path.expanduser(
                options.ghidra_scripts_install_dir))
        config.install_ghidra(options)
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
