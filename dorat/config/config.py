import os
import json
import requests
import re

def resolve_config():
    if not os.path.exists(CONFIG_FILE):
        print("Configuration json file not found in {}.".format(CONFIG_FILE))
        print("Please run --config to configure your ghidra application and scripts directory")
        print("Or run --install-ghidra to install ghidra and the ghidrascripts into the current directory")
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

def get_directory(prompt, default):
    print(prompt, f"({default}): ", end="")
    value = input()
    if value == "":
        return default
    var_subbed_path = value.format(**os.environ)
    resolved_value = os.path.realpath(os.path.expanduser(var_subbed_path))
    return resolved_value

def which(cmd):
    path = os.environ["PATH"]
    for path in path.split(":"):
        if os.path.exists(f"{path}/{cmd})"):
            return os.path.realpath(path)

def guess_java_path():
    java_path = which("java")
    if not java_path:
        return "JAVA NOT INSTALLED"
    return java_path

class MatchAction():
    def __init__(self, matcher, action):
        if type(matcher) == str:
            self.matcher = re.complie(matcher)
        else:
            self.matcher = matcher
        self.action = action  
        self.matches = []
    def match(self, path):
        if self.matcher.match(path.rsplit("/")[-1]):
            matches.append(path)
            return True
        return False
    def action(self, path):
        return action(path)

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

def find_ghidra_installs(start_dir):
    results = []
    matcher = MatchAction(r"ghidra_[0-9]*\.[0-9]*\.[0-9]*_PUBLIC", lambda p: [])
    for ghidra_install in dirwalk(stard_dir, action=matcher):

def configure_dorat():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    path_ghidra = get_directory("Path to Ghidra Root Directory", os.path.expanduser("~/"))
    path_scripts = get_directory("Path to Ghidra Scripts Directory", os.path.expanduser("~/"))
    java_home = get_directory("Path to Java Installation", guess_java_path())
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


