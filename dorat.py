#/usr/bin/env python3

import argparse
import subprocess
import os
import sys

GHIDRA_INSTALL_DIR=os.path.expanduser("~/installs/apps/ghidra_9.1.1_PUBLIC")
GHIDRA_SCRIPTS_DIR=os.path.expanduser("~/projects/hacking/ghidrascripts")

MARK_PREFIX = "INFO  {}> "
MARK_END = " (GhidraScript)  \n"

def parse_output(proc, options):
    state = "SCAN"
    mark_prefix = MARK_PREFIX.format(options.script)
    for line in iter(proc.stdout.readline, b''):
        line = str(line, 'utf8')
        if options.show_raw:
            sys.stdout.write(line)
        elif state == "SCAN":
            if line.startswith(mark_prefix):
                line = line.replace(mark_prefix, "")
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
    parser.add_argument("binary")
    parser.add_argument("script")
    parser.add_argument("--show-stderr", action="store_true")
    parser.add_argument("--show-raw", action="store_true")
    options, args = parser.parse_known_args()

    proc  = subprocess.Popen(["{}/support/analyzeHeadless".format(GHIDRA_INSTALL_DIR),
            '/tmp/', 'ProjectName',
            '-import', options.binary,
            '-deleteProject',
            '-scriptPath', GHIDRA_SCRIPTS_DIR,
            '-postScript', options.script,
            ]+args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    parse_output(proc, options)
    
main()
