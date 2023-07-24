import pytest

import dorat

import os
from tempfile import TemporaryDirectory

# need to figure out how to handlet this better
tmpdir = TemporaryDirectory()

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
    assert os.path.exists(f"{tempdir}/ghidrascripts/DecompileFunction.java")

def test_decompile(ghidra_install_dir):
    java_home = dorat.configuration.guess_java_path()
    config = {"JAVA_HOME": java_home, "GHIDRA_INSTALL_DIR": ghidra_install_dir+"/"+dorat.configuration.GHIDRA_VERSION, "GHIDRA_SCRIPTS_DIR": ghidra_install_dir + "/" + "ghidrascripts"}
    stdout, raw_stdout, stderr = dorat.dorat("DecompileFunction.java", "./data/test", ["main"], config)
    assert "Hello world" in stdout

