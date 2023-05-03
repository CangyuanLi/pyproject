import argparse
import typing
from typing import Optional

from .project_builder import Action, ProjectBuilder
from .__version__ import __version__

ACTIONS = list(typing.get_args(Action))
LICENSES = ("apache", "mit")


def _parse_arg_to_set(string: Optional[str], sep: str = ",") -> set[str]:
    """Expects a delimited string of arguments, e.g. `a,b,c,d`. Transforms string
    into a set.

    Args:
        string (Optional[str]): `a,b,c,d`
        sep (str): What to split on

    Returns:
        set[str]: string in set form
    """
    if string is None:
        return set()

    return set(word.strip() for word in string.split(sep))


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
        help="Reset configuration to default settings.",
    )
    parser.add_argument("--pypi_username", type=str, help="Set PyPI username")
    parser.add_argument("--pypi_password", type=str, help="Set PyPI password")
    parser.add_argument("--github_url", type=str, help="Set Github URL")
    parser.add_argument("--author", type=str, help="Set author name")
    parser.add_argument("--email", type=str, help="Set author email")
    parser.add_argument("--license", type=str, choices=LICENSES, help="Set license")
    parser.add_argument(
        "--set_dependencies",
        type=str,
        help=(
            "Set dependencies to always download. Overwrites saved config. Pass in a"
            " comma delimited string"
        ),
    )
    parser.add_argument(
        "--add_dependencies",
        type=str,
        help="Add dependencies to always download. Pass in a comma delimited string",
    )
    parser.add_argument(
        "--remove_dependencies",
        type=str,
        help="Remove dependencies to always download. Pass in a comma delimited string",
    )
    parser.add_argument(
        "--show", required=False, action="store_true", help="Show the current config"
    )
    parser.add_argument(
        "--quiet", required=False, action="store_true", help="Supress logging"
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

    options = {"quiet": args.quiet}

    config = {
        "pypi_username": args.pypi_username,
        "pypi_password": args.pypi_password,
        "github_url": args.github_url,
        "author": args.author,
        "email": args.email,
        "license": args.license,
        "set_dependencies": _parse_arg_to_set(args.set_dependencies),
        "add_dependencies": _parse_arg_to_set(args.add_dependencies),
        "remove_dependencies": _parse_arg_to_set(args.remove_dependencies),
        "reset_config": args.reset_config,
        "show": args.show,
    }

    builder = ProjectBuilder(config=config, options=options)
    builder.dispatch(action=args.action, project_name=args.project_name)


if __name__ == "__main__":
    main()
