#/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import json

import re
CONFIG_DIR = os.path.expanduser("~/.config/github.com/cwgreene/dorat/")
CONFIG_FILE = os.path.expanduser(CONFIG_DIR + "/dorat.json")

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

def configure_dorat():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    print("Path to Ghidra Root Directory: ", end="")
    path_ghidra = input()
    path_ghidra = os.path.expanduser(path_ghidra)
    print("Path to Ghidra Scripts Directory: ", end="")
    path_scripts = input()
    path_scripts = os.path.expanduser(path_scripts)
    with open(CONFIG_FILE, "w") as json_file:
        json.dump( {
            "version": "1",
            "GHIDRA_INSTALL_DIR":path_ghidra,
            "GHIDRA_SCRIPTS_DIR":path_scripts
        }, json_file)

def main():
    parser = argparse.ArgumentParser()
    main_group = parser.add_argument_group(title="main group")
    main_group.add_argument("--binary", help="REQUIRED: target binary")
    main_group.add_argument("--script", help="REQUIRED: target script")
    main_group.add_argument("--show-stderr", action="store_true", help="dump stderr")
    main_group.add_argument("--show-raw", action="store_true", help="dump raw output")
    list_group = parser.add_argument_group(title="list command")
    list_group.add_argument("--list", action="store_true", help="list scripts")
    list_group = parser.add_argument_group(title="configuration options")
    list_group.add_argument("--config", action="store_true", help="configure dorat")
    list_group.add_argument("--config-info", action="store_true", help="show dorat configuration in {}".format(CONFIG_FILE))
    options, args = parser.parse_known_args()

    if options.config_info:
        with open(CONFIG_FILE) as configfile:
            print(configfile.read())
        sys.exit(0)

    if options.config:
        configure_dorat()
        print("Dorat is configured. Enjoy!")
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

    proc  = subprocess.Popen(["{}/support/analyzeHeadless".format(config["GHIDRA_INSTALL_DIR"]),
            '/tmp/', 'ProjectName',
            '-import', options.binary,
            '-deleteProject',
            '-scriptPath', config["GHIDRA_SCRIPTS_DIR"],
            '-postScript', options.script,
            ]+args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    parse_output(proc, options)

main()
