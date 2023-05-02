# Imports

from __future__ import annotations

import dataclasses
import datetime
import os
import json
from pathlib import Path
import pprint
import re
import shutil
import subprocess
import string
from types import SimpleNamespace
from typing import Any, Literal, Optional, Union
import venv

import platformdirs

# Globals

BASE_PATH = Path(__file__).resolve().parents[0]
TEMPLATE_PATH = BASE_PATH / "templates"
USER_CONFIG_PATH = platformdirs.user_config_dir(
    appname="pyproject-generator", appauthor="cangyuanli"
)

# Types

Action = Literal["init", "upload", "config"]
PathLike = Union[Path, str]


@dataclasses.dataclass
class License:
    short_name: str
    proper_name: Optional[str] = None

    def __post_init__(self):
        if self.proper_name is None:
            name_mapper = {"mit": "MIT", "apache": "Apache", "gpl_v3": "GPL v3"}
            self.proper_name = name_mapper[self.short_name]


@dataclasses.dataclass
class Config:
    pypi_username: str
    pypi_password: str
    github_url: str
    author: str
    email: str
    license: License
    dependencies: set[str]

    def __post_init__(self):
        if isinstance(self.license, str):
            self.license = License(self.license)
        self.dependencies = set(self.dependencies)

    def to_json_representable(self) -> dict:
        _dict = self.to_dict()
        _dict["license"] = self.license.short_name
        _dict["dependencies"] = list(self.dependencies)

        return _dict

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def merge(cls, config1: Config, config2: Config):
        c1 = config1.to_dict()
        c2 = config2.to_dict()
        merged_config = {}
        for k, v in c1.items():
            if c2[k] is None:
                merged_config[k] = v
            else:
                merged_config[k] = c1[k]

        return Config(**merged_config)

    def __or__(self, config2: Config) -> Config:
        dct = self.to_dict() | config2.to_dict()

        return Config(**dct)


@dataclasses.dataclass
class CLIConfig(Config):
    set_dependencies: set[str]
    add_dependencies: set[str]
    remove_dependencies: set[str]
    reset_config: bool
    show: bool

    def __post_init__(self):
        self.dependencies = (
            self.dependencies | self.add_dependencies
        ) - self.remove_dependencies

        return super().__post_init__()


class Env(venv.EnvBuilder):
    def __init__(self, *args, **kwargs) -> None:
        self.context = self.get_context()
        super().__init__(*args, **kwargs)

    def get_context(self) -> Optional[SimpleNamespace]:
        if "VIRTUAL_ENV" not in os.environ:
            self.context = None
            return None

        env_dir = Path(os.environ["VIRTUAL_ENV"])
        env_name = env_dir.stem

        namespace = SimpleNamespace(
            env_dir=env_dir.as_posix(),
            env_name=env_name,
            bin_path=env_dir / "bin",
            env_exe=env_dir / "bin/python",
        )

        return namespace

    def post_setup(self, context: SimpleNamespace):
        # This sets self.context because `create()` calls `post_setup()`
        self.context = context

    def venv_create(self, venv_path: PathLike) -> Optional[SimpleNamespace]:
        self.create(venv_path)

        return self.context

    def run_bin(
        self, command: list[str], **kwargs
    ) -> subprocess.CompletedProcess[bytes]:
        # Run commands in the virtual environment. If context is not none, we are in
        # a virtual environment. Otherwise, let's just run it outside.
        if self.context is not None:
            command[0] = Path(self.context.bin_path).joinpath(command[0]).as_posix()

        return subprocess.run(command, check=True, **kwargs)


class ProjectBuilder:
    def __init__(
        self,
        template_path: PathLike = TEMPLATE_PATH,
        user_config_dir: PathLike = USER_CONFIG_PATH,
        config: dict[str, str] = None,
    ) -> None:
        self.proj_path = Path().cwd()

        self._template_path = Path(template_path)

        self._user_config_dir = Path(user_config_dir)
        self._create_config_dir()
        self._config = self._set_config(config)

    @staticmethod
    def _validate_project_name(project_name: str) -> None:
        # https://packaging.python.org/en/latest/specifications/name-normalization/
        regex = "^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$"
        if not bool(re.match(regex, project_name, re.IGNORECASE)):
            raise ValueError(
                "A valid project name may only contain ASCII letters, numbers, ., -,"
                " and/or _, and they must begin and end with a letter or number."
            )

    def _create_config_dir(self) -> None:
        """Create the user config directory if it does not exist. Since the default
        configuration may add keys, merge the two, preferring the
        existing config so we don't overwrite user changes.
        """
        self._user_config_dir.mkdir(exist_ok=True)
        config_file = self._user_config_dir / "config.json"

        if not config_file.exists() or config_file.stat().st_size == 0:
            shutil.copy(
                BASE_PATH / "config/default_config.json",
                config_file,
            )

        config = self._parse_config_file("config.json")
        default_config = self._parse_config_file("default_config.json")

        config = default_config | config
        self._write_config_file(config)

        return None

    def _fill_in_templates(self, project_name: str) -> dict[str, str]:
        """Loop through the the templates folder and fill in data.

        Args:
            project_name (str): User-supplied project name

        Returns:
            dict[str, str]: {file_stem: filled_in_template}
        """
        config = self._config
        d = {
            "PACKAGE": project_name,
            "PYPI_USERNAME": config.pypi_username,
            "PYPI_PASSWORD": config.pypi_password,
            "GITHUB_URL": config.github_url,
            "AUTHOR": config.author,
            "EMAIL": config.email,
            "YEAR": datetime.datetime.now().year,
            "LICENSE": config.license.proper_name,
        }

        filled_in_templates = {}
        for file in self._template_path.glob("*.template"):
            with open(file, "r") as f:
                src = string.Template(f.read())
                result = src.substitute(d)

                filled_in_templates[file.stem] = result

        return filled_in_templates

    def init_project(self, project_name: str):
        """Called when user specifies `action = init`.

        Args:
            project_name (str): User-supplied name of project
        """
        # Create the project directory
        self._validate_project_name(project_name)

        proj_path = self.proj_path / project_name
        proj_path.mkdir()

        # src
        src_path = proj_path / "src"
        src_path.mkdir()

        src_proj_path = src_path / project_name
        src_proj_path.mkdir()
        (src_proj_path / "__init__.py").touch()
        (src_proj_path / "py.typed").touch()

        # Fill in templates
        templates = self._fill_in_templates(project_name)

        # tests
        tests_path = proj_path / "tests"
        tests_path.mkdir()
        (tests_path / f"test_{project_name}.py").touch()

        # benchmarks
        benchmarks_path = proj_path / "benchmarks"
        benchmarks_path.mkdir()
        (benchmarks_path / "benchmark.py").touch()

        # github actions
        workflows_path = proj_path / ".github/workflows"
        workflows_path.mkdir(parents=True)
        (workflows_path / "tests.yml").write_text(templates["tests"])

        # misc setup
        (proj_path / "tox.ini").write_text(templates["tox"])
        (proj_path / "pyproject.toml").write_text(templates["pyproject"])
        (proj_path / "setup.cfg").write_text(templates["setup"])
        (proj_path / ".gitignore").write_text(templates["gitignore"])
        (proj_path / "README.md").write_text(templates["readme"])

        license = self._config.license.short_name
        (proj_path / "LICENSE").write_text(templates[f"license_{license}"])

        # Setup the virtual environment

        venv_builder = Env(with_pip=True)
        venv_builder.venv_create(proj_path / "venv")
        venv_builder.run_bin(["python", "-m", "pip", "install", "-U", "pip"])

        # Install developer dependencies
        for dep in self._config.dependencies:
            venv_builder.run_bin(["pip", "install", dep])

        # Create requirements_dev file
        reqs = venv_builder.run_bin(["pip", "freeze"], capture_output=True)
        (proj_path / "requirements_dev.txt").write_bytes(reqs.stdout)

    def _parse_config_file(self, filename: PathLike) -> Config:
        if filename == "default_config.json":
            path = BASE_PATH / "config/default_config.json"
        elif filename == "config.json":
            path = self._user_config_dir / filename
        else:
            raise ValueError("Name wrong.")

        with open(path) as f:
            config: dict = json.load(f)

        return Config(**config)

    def _set_config(self, config: dict[str, str]) -> Config:
        """Take in the arguments provided by the user and merge them with their
        saved configuration file.

        Args:
            config (dict[str, str]): Expects either the saved user
            configuration or the default configuration (if --reset flag is set).

        Returns:
            dict: A configuration dict of {config_arg: config}
        """
        if config["reset_config"]:
            saved_path = "default_config.json"
        else:
            saved_path = "config.json"

        saved_config = self._parse_config_file(saved_path)

        # --set_dependencies overrides the saved dependencies. So simply use saved
        # if flag is not set, otherwise parse the list of provided dependencies.
        if config["set_dependencies"] is None:
            config["dependencies"] = saved_config.dependencies
        else:
            config["dependencies"] = config["set_dependencies"]

        _config = CLIConfig(**config)

        merged_config = Config.merge(saved_config, _config)

        if _config.show:
            pprint.pprint(merged_config.to_json_representable())

        return merged_config

    def _write_config_file(self, config: Config):
        with open(self._user_config_dir / "config.json", "w") as f:
            json.dump(config.to_json_representable(), f, indent=4)

    def config(self):
        """If the action is `config`, save the built configuration as the default. This
        method is intentionally sparse, as the bulk of the work should be done by
        creating the config on the fly--we want the user to be able to pass config flags
        in without going through the config action.
        """
        self._write_config_file(self._config)

    def upload(self):
        """Discover the virtual environment and upload project to PyPI."""
        username = self._config["pypi_username"]
        password = self._config["pypi_password"]

        env = Env()

        # python -m build generates a dist folder, remove this in preparation
        shutil.rmtree(self.proj_path / "dist", ignore_errors=True)

        env.run_bin(["python", "-m", "build"])
        env.run_bin(["twine", "check", "dist/*"])

        if username == "" and password == "":
            twine_args = []
        elif username == "" and password != "":
            twine_args = ["-p", password]
            env.run_bin(["twine", "upload", "dist/*", "-p", password])
        elif username != "" and password == "":
            twine_args = ["-u", username]
        else:
            twine_args = ["-u", username, "-p", password]

        env.run_bin(["twine", "upload", "dist/*"] + twine_args)

    def dispatch(self, action: Action, **kwargs):
        if action == "init":
            self.init_project(**kwargs)
        elif action == "upload":
            self.upload()
        elif action == "config":
            self.config()
