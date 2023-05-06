import pytest

import pyproject.logger as logger
import pyproject.project_builder as pb

CONFIG1: dict = {
    "pypi_username": None,
    "pypi_password": None,
    "github_url": None,
    "author": None,
    "email": None,
    "license": None,
    "set_dependencies": set(),
    "add_dependencies": set(),
    "remove_dependencies": set(),
    "reset_config": False,
    "show": False,
}

CONFIG2: dict = {
    "pypi_username": "username",
    "pypi_password": "password",
    "github_url": "url",
    "author": "author",
    "email": "email",
    "license": "apache",
    "set_dependencies": {"black", "ruff", "pytest"},
    "add_dependencies": {"white"},
    "remove_dependencies": {"black"},
    "reset_config": False,
    "show": False,
}


def test_parse_config_file():
    builder = pb.ProjectBuilder(config=CONFIG1, options={}, logger=logger.Level.INFO)
    with pytest.raises(ValueError):
        builder._parse_config_file("default_config")

    assert builder._parse_config_file("default_config.json") == pb.Config(
        pypi_username="",
        pypi_password="",
        github_url="",
        author="",
        email="",
        license="mit",
        dependencies=[
            "black",
            "build",
            "isort",
            "mypy",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "ruff",
            "tox",
            "twine",
        ],
    )


def test_config_resolution():
    builder = pb.ProjectBuilder(config=CONFIG2, options={}, logger=logger.Level.INFO)
    assert builder._config == pb.Config(
        pypi_username="username",
        pypi_password="password",
        github_url="url",
        author="author",
        email="email",
        license="apache",
        dependencies={"white", "ruff", "pytest"},
    )
