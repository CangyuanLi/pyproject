# Imports

from pathlib import Path
import re
import subprocess
import string
from types import SimpleNamespace
from typing import Literal, Optional, Union
import venv

Action = Literal["init", "upload", "config"]
PathLike = Union[Path, str]

TEMPLATE_PATH = Path(__file__).resolve().parents[0] / "templates"


class _EnvBuilder(venv.EnvBuilder):
    def __init__(self, venv_path: PathLike, *args, **kwargs) -> None:
        self.context: Optional[SimpleNamespace] = None
        self.venv_path = Path(venv_path)
        super().__init__(*args, **kwargs)

    def post_setup(self, context: SimpleNamespace):
        self.context = context

    def venv_create(self) -> Optional[SimpleNamespace]:
        self.create(self.venv_path)

        return self.context

    def run_python_in_venv(
        self, command: list[str]
    ) -> subprocess.CompletedProcess[bytes]:
        assert self.context is not None
        command = [self.context.env_exe] + command

        return subprocess.run(command, check=True)

    def run_bin_in_venv(
        self, command: list[str], **kwargs
    ) -> subprocess.CompletedProcess[bytes]:
        assert self.context is not None
        command[0] = Path(self.context.bin_path).joinpath(command[0]).as_posix()

        return subprocess.run(command, check=True, **kwargs)


def _venv_create(venv_path):
    venv_builder = _EnvBuilder(with_pip=True)
    venv_builder.create(venv_path)

    return venv_builder.context


def _run_python_in_venv(venv_context: SimpleNamespace, command: list[str]):
    command = [venv_context.env_exe] + command

    return subprocess.run(command, check=True)


def _run_bin_in_venv(venv_context: SimpleNamespace, command: list[str]):
    command[0] = Path(venv_context.bin_path).joinpath(command[0]).as_posix()

    return subprocess.run(command, check=True, capture_output=True)


class ProjectBuilder:
    def __init__(
        self, project_name: str, template_path: PathLike = TEMPLATE_PATH
    ) -> None:
        self._validate_project_name(project_name)
        self._project_name = project_name
        self._project_path = Path(project_name)
        self._template_path = Path(template_path)

    @staticmethod
    def _validate_project_name(project_name: str) -> None:
        regex = "^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$"
        if not bool(re.match(regex, project_name, re.IGNORECASE)):
            raise ValueError(
                "A valid project name may only contain ASCII letters, numbers, ., -,"
                " and/or _, and they must begin and end with a letter or number."
            )

    def fill_in_templates(self) -> dict[str, str]:
        d = {"PACKAGE": self._project_name}
        filled_in_templates = {}
        for file in self._template_path.glob("*.template"):
            with open(file, "r") as f:
                src = string.Template(f.read())
                result = src.substitute(d)

                filled_in_templates[file.stem] = result

        return filled_in_templates

    def init_project(self):
        # Create the project directory
        self._project_path.mkdir()

        # src
        src_path = self._project_path / "src"
        src_path.mkdir()

        src_proj_path = src_path / self._project_name
        src_proj_path.mkdir()
        (src_proj_path / "__init__.py").touch()
        (src_proj_path / "py.typed").touch()

        # Fill in templates
        templates = self.fill_in_templates()

        # tests
        tests_path = self._project_path / "tests"
        tests_path.mkdir()
        (tests_path / f"test_{self._project_name}.py").touch()

        # benchmarks
        benchmarks_path = self._project_path / "benchmarks"
        benchmarks_path.mkdir()
        (benchmarks_path / "benchmark.py").touch()

        # github actions
        workflows_path = self._project_path / ".github/workflows"
        workflows_path.mkdir(parents=True)
        (workflows_path / "tests.yml").write_text(templates["tests"])

        # misc setup
        (self._project_path / "tox.ini").write_text(templates["tox"])
        (self._project_path / "pyproject.toml").write_text(templates["pyproject"])
        (self._project_path / "setup.cfg").write_text(templates["setup"])
        (self._project_path / ".gitignore").write_text(templates["gitignore"])
        (self._project_path / "README.md").write_text(templates["readme"])

        # Setup the virtual environment

        venv_builder = _EnvBuilder(self._project_path / "venv", with_pip=True)
        venv_builder.venv_create()
        venv_builder.run_python_in_venv(["-m", "pip", "install", "-U", "pip"])

        # Install developer dependencies
        for dep in ("black", "mypy", "build", "tox", "pytest"):
            venv_builder.run_bin_in_venv(["pip", "install", dep])

        # Create requirements_dev file
        reqs = venv_builder.run_bin_in_venv(["pip", "freeze"], capture_output=True)
        (self._project_path / "requirements_dev.txt").write_bytes(reqs.stdout)

    def dispatch(self, action: Action):
        if action == "init":
            self.init_project()
        elif action == "upload":
            raise NotImplementedError("Uploading a project is not supported yet.")
        elif action == "config":
            raise NotImplementedError(
                "Setting environment variables is not supported yet."
            )
