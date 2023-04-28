import argparse
import typing

from .project_builder import Action, ProjectBuilder
from .__version__ import __version__

ACTIONS = list(typing.get_args(Action))


def get_parser():
    parser = argparse.ArgumentParser(description="Generate python project")

    parser.add_argument("action", type=str, choices=ACTIONS, help="Action")
    parser.add_argument(
        "project_name", type=str, nargs="?", default=None, help="Name of the project"
    )

    parser.add_argument(
        "--reset_config",
        required=False,
        action="store_true",
        help="Reset configuration to default settings",
    )
    parser.add_argument("--pypi_username", type=str, help="Set PyPI username")
    parser.add_argument("--pypi_password", type=str, help="Set PyPI password")
    parser.add_argument("--github_url", type=str, help="Set Github URL")
    parser.add_argument("--author", type=str, help="Set author name")
    parser.add_argument("--email", type=str, help="Set author email")
    parser.add_argument(
        "--set_dependencies",
        type=str,
        help=(
            "Set dependencies to always download. Overwrites saved config. Pass in a"
            " comma delimited string."
        ),
    )
    parser.add_argument(
        "--add_dependencies",
        type=str,
        help="Add dependencies to always download. Pass in a comma delimited string.",
    )
    parser.add_argument(
        "--remove_dependencies",
        type=str,
        help=(
            "Remove dependencies to always download. Pass in a comma delimited string."
        ),
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
        help="Displays package version",
    )

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.action == "init" and args.project_name is None:
        parser.error("init requires project name")

    config: dict[str, str] = {
        "pypi_username": args.pypi_username,
        "pypi_password": args.pypi_password,
        "github_url": args.github_url,
        "author": args.author,
        "email": args.email,
        "set_dependencies": args.set_dependencies,
        "add_dependencies": args.add_dependencies,
        "remove_dependencies": args.remove_dependencies,
        "reset_config": args.reset_config,
    }

    builder = ProjectBuilder(config=config)
    builder.dispatch(action=args.action, project_name=args.project_name)


if __name__ == "__main__":
    main()
