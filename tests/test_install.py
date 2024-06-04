import pytest

import dorat

import os
import subprocess
from tempfile import TemporaryDirectory, mkdtemp

# need to figure out how to handlet this better
tmpdir = TemporaryDirectory()

# TODO: this is the way to implement "delete=False"
# until we start using python 3.12.
#class TempDir:
#    def __init__(self):
#        res = mkdtemp()
#        self.name = res
#tmpdir = TempDir()

@pytest.fixture
def ghidra_install_dir():
    yield tmpdir.name

def test_install(ghidra_install_dir):
    tempdir = ghidra_install_dir
    options = dorat.configuration.GhidraOptions(True, tempdir, tempdir+"/ghidrascripts")
    dorat.configuration.install_ghidra(options)
    assert os.path.exists(f"{tempdir}/{dorat.configuration.GHIDRA_VERSION}")
    assert os.path.exists(f"{tempdir}/{dorat.configuration.GHIDRA_VERSION}/support/analyzeHeadless")
    assert os.path.exists(f"{tempdir}/ghidrascripts")
    # this should probably be better setup by creating some sort of testing validation of
    # ghidra scripts itself... but its a bit of a chicken and egg problem that.
    # cant easily test that ghidrascripts is working without dorat.
    # so this is basically the bare minimum we can validate.
    assert os.path.exists(f"{tempdir}/ghidrascripts/install.sh")
    assert os.path.exists(f"{tempdir}/ghidrascripts/scripts/java/DecompileFunction.java")
    assert subprocess.run(["git", "-C", f"{tempdir}/ghidrascripts", "rev-parse", "HEAD"], capture_output=True).stdout == b"ac90be33be86e6811741c528c4f4fa55eefb1139\n"

def test_decompile(ghidra_install_dir):
    java_home = dorat.configuration.guess_java_path()
    config = {
        "GHIDRA_VERSION": dorat.configuration.GHIDRA_VERSION,
        "JAVA_HOME": java_home,
        "GHIDRA_INSTALL_DIR": ghidra_install_dir,
        "GHIDRA_SCRIPTS_DIR": ghidra_install_dir + "/" + "ghidrascripts"
    }
    stdout, raw_stdout, stderr = dorat.dorat("DecompileFunction.java", "./data/test", ["main"], config)
    print("raw_stdout", stdout)
    print("stderr", stderr)
    assert "Hello world" in stdout

