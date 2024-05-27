import os

CONFIG_DIR = os.path.expanduser("~/.config/github.com/cwgreene/dorat/")
CONFIG_FILE = os.path.expanduser(CONFIG_DIR + "/dorat.json")

def is_dorat_configured(config_file_path=CONFIG_FILE):
    if not os.path.exists(config_file_path):
        return False
    with open(config_file_path) as config_file:
        data = config_file.read()
        js = json.loads(data)
        if "GHIDRA_INSTALL_DIR" in js and "GHIDRA_SCRIPTS_DIR" in js:
            return True
    return False
