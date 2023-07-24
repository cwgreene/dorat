import pytest

import dorat

import os
from tempfile import TemporaryDirectory

@pytest.fixture
def ghidra_install_dir():
    tmpdir = TemporaryDirectory()
    yield tmpdir.name
    tmpdir.cleanup()

def test_install(ghidra_install_dir):
    tempdir = ghidra_install_dir
    options = dorat.configuration.GhidraOptions(True, tempdir, tempdir+"/ghidrascripts")
    dorat.configuration.install_ghidra(options)
    assert os.path.exists(f"{tempdir}/{dorat.configuration.GHIDRA_VERSION}")
    assert os.path.exists(f"{tempdir}/ghidrascripts")
    # this should probably be better setup by creating some sort of testing validation of
    # ghidra scripts itself... but its a bit of a chicken and egg problem that.
    # cant easily test that ghidrascripts is working without dorat.
    # so this is basically the bare minimum we can validate.
    assert os.path.exists(f"{tempdir}/ghidrascripts/install.sh")
    assert os.path.exists(f"{tempdir}/ghidrascripts/DecompileFunction.java")
