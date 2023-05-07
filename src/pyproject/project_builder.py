# Imports

from __future__ import annotations

import dataclasses
import datetime
import json
import os
import re
import shutil
import string
import subprocess
import venv
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, Optional, Union

import platformdirs
from rich.panel import Panel

from .licenses import LICENSES, License
from .logger import Logger
from .utils import squash_collection

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
            self.license = LICENSES[self.license]
        self.dependencies = set(self.dependencies)

    def to_json_representable(self) -> dict:
        _dict = self.to_dict()
        _dict["license"] = self.license.short_name
        _dict["dependencies"] = sorted(list(self.dependencies))

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
                merged_config[k] = c2[k]

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
        config: dict,
        options: dict,
        logger: Logger,
        template_path: PathLike = TEMPLATE_PATH,
        user_config_dir: PathLike = USER_CONFIG_PATH,
    ) -> None:
        self.proj_path = Path().cwd()

        self._template_path = Path(template_path)
        self._logger = logger

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
            "LICENSE_BADGE": config.license.badge_url,
            "LICENSE_LINK": config.license.link,
        }

        filled_in_templates = {}
        for file in self._template_path.glob("*.template"):
            with open(file, "r") as f:
                src = string.Template(f.read())
                result = src.substitute(d)

                filled_in_templates[file.stem] = result

        return filled_in_templates

    @staticmethod
    def _init_git(proj_path: Path):
        subprocess.run(["git", "init"], cwd=proj_path, stdout=subprocess.DEVNULL)

    @staticmethod
    def _init_source_directory(proj_path: Path, project_name: str):
        src_path = proj_path / "src"
        src_path.mkdir()

        src_proj_path = src_path / project_name
        src_proj_path.mkdir()
        (src_proj_path / "__init__.py").touch()
        (src_proj_path / "py.typed").touch()

        version_file = src_proj_path / "__version__.py"
        version_file.touch()
        version_file.write_text('__version__ = "0.0.0"')

    @staticmethod
    def _init_tests(proj_path: Path, project_name: str):
        tests_path = proj_path / "tests"
        tests_path.mkdir()
        (tests_path / f"test_{project_name}.py").touch()

    @staticmethod
    def _init_benchmarks(proj_path: Path):
        benchmarks_path = proj_path / "benchmarks"
        benchmarks_path.mkdir()
        (benchmarks_path / "benchmark.py").touch()

    def _init_config_files(self, proj_path: Path, templates: dict):
        (proj_path / "tox.ini").write_text(templates["tox"])
        (proj_path / "pyproject.toml").write_text(templates["pyproject"])
        (proj_path / "setup.cfg").write_text(templates["setup"])
        (proj_path / ".gitignore").write_text(templates["gitignore"])
        (proj_path / "README.md").write_text(templates["readme"])
        (proj_path / ".pre-commit-config.yaml").write_text(
            templates["pre_commit_config"]
        )

        license = self._config.license.short_name
        (proj_path / "LICENSE").write_text(templates[f"license_{license}"])

    @staticmethod
    def _init_github_actions(proj_path, templates: dict):
        workflows_path = proj_path / ".github/workflows"
        workflows_path.mkdir(parents=True)
        (workflows_path / "tests.yaml").write_text(templates["tests"])

    def init_project(self, project_name: str):
        """Called when user specifies `action = init`.

        Args:
            project_name (str): User-supplied name of project
        """

        # Create the project directory
        try:
            self._validate_project_name(project_name)
        except ValueError as e:
            self._logger.error(str(e))

        proj_path = self.proj_path / project_name

        try:
            proj_path.mkdir()
        except FileExistsError:
            self._logger.error(f"{proj_path} already exists")

        self._logger.info(Panel("Creating project files..."), justify="left")

        # Fill in templates
        templates = self._logger.spinner(
            lambda: self._fill_in_templates(project_name),
            "Filling in templates",
        )

        # initialize git repo
        self._logger.spinner(
            lambda: self._init_git(proj_path),
            "Initializing git repository",
        )

        # src
        self._logger.spinner(
            lambda: self._init_source_directory(proj_path, project_name),
            "Creating source directory",
        )

        # tests
        self._logger.spinner(
            lambda: self._init_tests(proj_path, project_name),
            "Creating tests",
        )

        # benchmarks
        self._logger.spinner(
            lambda: self._init_benchmarks(proj_path),
            "Creating benchmarks",
        )

        # github actions
        self._logger.spinner(
            lambda: self._init_github_actions(proj_path, templates),
            "Setting up Github Actions",
        )

        # misc setup
        self._logger.spinner(
            lambda: self._init_config_files(proj_path, templates),
            "Setting up configuration files",
        )

        self._logger.info("Building project skeleton completed with no errors.")

        # Setup the virtual environment
        self._logger.info(
            Panel("Setting up the virtual environment..."), justify="left"
        )

        venv_builder = Env(with_pip=True)
        venv_builder.venv_create(proj_path / "venv")

        # Install developer dependencies

        self._logger.spinner(
            lambda: venv_builder.run_bin(
                ["python", "-m", "pip", "install", "-U", "pip"],
                stdout=subprocess.DEVNULL,
            ),
            text="pip",
            clear=False,
        )

        not_installed = []
        for dep in sorted(list(self._config.dependencies)):
            try:
                self._logger.spinner(
                    lambda: venv_builder.run_bin(
                        ["pip", "install", dep],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    ),
                    text=dep,
                    clear=False,
                )
            except subprocess.CalledProcessError:
                not_installed.append(dep)

        if len(not_installed) > 0:
            self._logger.warning(
                f"Failed to install {squash_collection(not_installed)}"
            )

        self._logger.info(Panel("Finalizing project..."), justify="left")

        # Create requirements_dev file
        def _create_req_file():
            reqs = venv_builder.run_bin(["pip", "freeze"], capture_output=True)
            (proj_path / "requirements_dev.txt").write_bytes(reqs.stdout)

        self._logger.spinner(
            _create_req_file,
            "Creating requirements_dev.txt",
        )

        if (
            "pre-commit" in self._config.dependencies
            and "pre-commit" not in not_installed
        ):
            # Ensure pre-commit is up to date
            self._logger.spinner(
                lambda: venv_builder.run_bin(
                    ["pre-commit", "autoupdate"],
                    cwd=proj_path,
                    stdout=subprocess.DEVNULL,
                ),
                "Ensuring pre-commit config is up to date",
                clear=True,
            )

            # Install pre-commit hooks
            self._logger.spinner(
                lambda: venv_builder.run_bin(
                    ["pre-commit", "install"], cwd=proj_path, stdout=subprocess.DEVNULL
                ),
                "Installing pre-commit hooks",
                clear=True,
            )

        self._logger.info(f"Done setting up {project_name}!", style="green")

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

    def _set_config(self, config: dict) -> Config:
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
        if len(config["set_dependencies"]) == 0:
            config["dependencies"] = saved_config.dependencies
        else:
            config["dependencies"] = config["set_dependencies"]

        _config = CLIConfig(**config)

        merged_config = Config.merge(saved_config, _config)

        if _config.show:
            self._logger.pprint(merged_config.to_json_representable())

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
        username = self._config.pypi_username
        password = self._config.pypi_password

        env = Env()

        # python -m build generates a dist folder, remove this in preparation
        self._logger.spinner(
            lambda: shutil.rmtree(self.proj_path / "dist", ignore_errors=True),
            "Removing existing build",
            prefix="",
            clear=False,
        )

        self._logger.spinner(
            lambda: env.run_bin(["python", "-m", "build"], stdout=subprocess.DEVNULL),
            "Building project",
            prefix="",
            clear=False,
        )
        self._logger.spinner(
            lambda: env.run_bin(
                ["twine", "check", "dist/*"], stdout=subprocess.DEVNULL
            ),
            "Checking build",
            prefix="",
            clear=False,
        )

        if username == "" and password == "":
            twine_args = []
        elif username == "" and password != "":
            twine_args = ["-p", password]
        elif username != "" and password == "":
            twine_args = ["-u", username]
        else:
            twine_args = ["-u", username, "-p", password]

        # Upload to pypi
        self._logger.info("\n", end="")

        # allow twine to use its own errors
        try:
            env.run_bin(["twine", "upload", "dist/*"] + twine_args)
        except subprocess.CalledProcessError:
            pass

    def dispatch(self, action: Action, **kwargs):
        if action == "init":
            self.init_project(**kwargs)
        elif action == "upload":
            self.upload()
        elif action == "config":
            self.config()
