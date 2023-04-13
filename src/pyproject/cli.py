import argparse
import typing

from .project_builder import Action, ProjectBuilder
from .__version__ import __version__

ACTIONS = list(typing.get_args(Action))


def get_parser():
    parser = argparse.ArgumentParser(description="Generate python project")

    parser.add_argument("action", type=str, choices=ACTIONS, help="Action")
    parser.add_argument("project_name", type=str, help="Name of the project")

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
        help="Displays package version",
    )

    return parser


def main():
    args = get_parser().parse_args()

    a = ProjectBuilder(project_name=args.project_name)
    a.init_project()


if __name__ == "__main__":
    main()
