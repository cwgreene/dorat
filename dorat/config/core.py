import os
import json
import requests
import re
import sys

import zipfile

from tempfile import TemporaryDirectory
from . import ghidra as ghidra_config
from .shared import CONFIG_DIR, CONFIG_FILE, CONFIG_VERSION

from enum import Enum

# Exceptions
class OldVersionException(Exception):
    def __init__(self, msg, old_js):
        super().__init__(msg)
        self.old_js = old_js

class ConfigFields(str, Enum):
    name = "name"
    GHIDRA_INSTALL_DIR = "GHIDRA_INSTALL_DIR"
    GHIDRA_SCRIPTS_DIR = "GHIDRA_SCRIPTS_DIR"
    GHIDRA_VERSION = "GHIDRA_VERSION"
    JAVA_HOME = "JAVA_HOME"

def resolve_config(config_file_path=CONFIG_FILE, group="default"):
    if not os.path.exists(config_file_path):
        print("Configuration json file not found in {}.".format(config_file_path))
        print("Please run --config to configure your ghidra application and scripts directory")
        print("Or run --install-ghidra to install ghidra and the ghidrascripts into the current directory")
        sys.exit(1)
    try:
        return find_group(load_config(config_file_path), group)
    except OldVersionException as old_version:
        print(f"{old_version}")
        print(f"Config version of {config_file_path} is out of date")
        print("Run '--config' to update")
        sys.exit(1)

def minimal_config():
    return {
        "version": CONFIG_VERSION,
        "groups": []
    }

def find_group(config, name):
    for _, group in enumerate(config["groups"]):
        if group["name"] == name:
            return group
    return None

def update_group(config, name, updated_group):
    for i, group in enumerate(config["groups"]):
        if group["name"] == name:
            break
    else:
        config["groups"].append(updated_group)
        return
    config["groups"][i] = updated_group

def load_config(config_file_path=CONFIG_FILE):
    if not os.path.exists(config_file_path):
        return minimal_config()
    with open(config_file_path) as config_file:
        js = json.load(config_file)
        if (version:=js["version"]) != CONFIG_VERSION:
            raise OldVersionException(f"Configuration file version '{version}' is not '{CONFIG_VERSION}'", js)
    return js

def write_group_to_config(group, old_config, path_ghidra, path_scripts, ghidra_version, java_home, config_file_path=CONFIG_FILE):
    new_group = {
        ConfigFields.name: group,
        ConfigFields.GHIDRA_INSTALL_DIR: path_ghidra,
        ConfigFields.GHIDRA_SCRIPTS_DIR: path_scripts,
        ConfigFields.GHIDRA_VERSION: ghidra_version,
        ConfigFields.JAVA_HOME: java_home
    }
    update_group(old_config, group, new_group)
    with open(config_file_path, "w") as json_file:
        json_file.write(json.dumps(old_config,indent=2))

def get_directory(prompt, default):
    print(prompt, f"({default}): ", end="")
    value = input()
    if value == "":
        return default
    var_subbed_path = value.format(**os.environ)
    resolved_value = os.path.realpath(os.path.expanduser(var_subbed_path))
    return resolved_value

def get_value(prompt, default):
    print(prompt, f"({default}): ", end="")
    value = input()
    if value == "":
        return default
    return value

def which(cmd):
    path = os.environ["PATH"]
    for path in path.split(":"):
        p = f"{path}/{cmd}"
        if os.path.exists(p):
            return os.path.realpath(p)

def guess_java_path():
    java_path = which("java")
    if not java_path:
        return "JAVA NOT INSTALLED"
    return java_path

def dirwalk(start_dir, max_depth=None, cur_depth=0, exclude=[".git"],action=None):
    for file in os.listdir(start_dir):
        path = start_dir + "/" + file
        if action and action.match(path):
                yield from action.action(path)
        elif os.path.isdir(path):
            yield path
            if file not in exclude:
                yield from dirwalk(path, max_depth, cur_depth + 1, exclude)
        else:
            yield path

def upgrade_dorat(old_js):
    assert old_js["version"] == "1"
    new_js = {"version": "2"}
    new_js["groups"] = [old_js]
    new_js["groups"][0]["name"] = "default"
    return new_js

def configure_dorat(config_file_path=None):
    if config_file_path is None:
        config_file_path = os.path.expanduser(CONFIG_DIR + "/dorat.json")
    dirs = os.path.dirname(config_file_path)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    cur_config = {"version":"2", "groups": [{}]}
    if os.path.exists(config_file_path):
        # try to load existing
        try:
            cur_config = load_config(config_file_path)
        except OldVersionException as exception:
            cur_config = upgrade_dorat(exception.old_js)
    cur_config_group = cur_config["groups"][0]
    ghidra_version = get_value("Ghidra Version",
        cur_config_group.get("GHIDRA_VERSION", ghidra_config.GHIDRA_VERSION))
    path_ghidra = get_directory("Path to Ghidra Root Directory",
        cur_config_group.get("GHIDRA_INSTALL_DIR", os.path.expanduser("~/")))
    path_scripts = get_directory("Path to Ghidra Scripts Directory",
        cur_config_group.get("GHIDRA_SCRIPTS_DIR", os.path.expanduser("~/")))
    java_home = get_directory("Path to Java Installation",
        cur_config_group.get("JAVA_HOME", guess_java_path()))
    write_group_to_config("default", cur_config, path_ghidra, path_scripts, ghidra_version, java_home, config_file_path=config_file_path)

