import shutil
import subprocess
from pathlib import Path

import pytest

from pyproject.cli import ALLOWED_LICENSES

BASE_PATH = Path(__file__).resolve().parents[1]
TEMP_PATH = BASE_PATH / "tmpdir"


def _create_tmpdir():
    shutil.rmtree(TEMP_PATH, ignore_errors=True)
    TEMP_PATH.mkdir()
    TEMP_PATH.cwd()


def _remove_tmpdir():
    shutil.rmtree(TEMP_PATH)


_create_tmpdir()


@pytest.mark.parametrize(
    "call",
    [
        ["pyproject", "init"],
        ["pyproject", "blah"],
        ["pyproject", "config", "--license=tim"],
    ],
)
def test_input_validation(call):
    process = subprocess.run(call)
    assert process.returncode == 1


@pytest.mark.parametrize("license", ALLOWED_LICENSES)
def test_licenses(license):
    process = subprocess.run(
        ["pyproject", "init", "tmp", f"--license={license}", "--set_dependencies=pip"],
        cwd=TEMP_PATH,
    )
    shutil.rmtree(TEMP_PATH / "tmp")
    assert process.returncode == 0


def test_cleanup():
    _remove_tmpdir()
