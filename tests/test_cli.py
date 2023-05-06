import subprocess

import pytest


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
