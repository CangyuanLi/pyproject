# Imports

from pathlib import Path
import re
import shutil
import string
from typing import Literal, Union


Action = Literal["init", "convert"]
PathLike = Union[Path, str]

TEMPLATE_PATH = Path(__file__).resolve().parents[0] / "templates"


class ProjectBuilder:
    def __init__(
        self, project_name: str, template_path: PathLike = TEMPLATE_PATH
    ) -> None:
        self._validate_project_name(project_name)
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

    def fill_in_templates(self):
        for file in self._template_path.glob("*.template"):
            with open(file) as f:
                src = string.Template(f.read())

    def init_project(self):
        # Create the project directory
        self._project_path.mkdir()

        shutil.copy(
            self._template_path / "setup.template", self._project_path / "setup.cfg"
        )
        shutil.copy(self._temp)

    def create_project(self, action: Action):
        if action == "init":
            pass
        elif action == "convert":
            raise NotImplementedError(
                "Converting an existing project is not supported yet."
            )
