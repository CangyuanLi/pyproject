import argparse
import re
import typing
from typing import Optional

from .__version__ import __version__
from .licenses import LICENSES
from .logger import Level, Logger
from .project_builder import Action, ProjectBuilder

ACTIONS = typing.get_args(Action)
ALLOWED_LICENSES = tuple(LICENSES.keys())


def _validate_project_name(project_name: str) -> None:
    # https://packaging.python.org/en/latest/specifications/name-normalization/
    regex = "^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$"
    if not bool(re.match(regex, project_name, re.IGNORECASE)):
        raise ValueError(
            "A valid project name may only contain ASCII letters, numbers, ., -,"
            " and/or _, and they must begin and end with a letter or number."
        )


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

    parser.add_argument("action", type=str, help="Action")
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
    parser.add_argument(
        "--license",
        type=str,
        help=f"Set license. Available licenses are {ALLOWED_LICENSES}",
    )
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


def _validate_input(args, logger: Logger):
    if args.action not in ACTIONS:
        logger.error(f"Invalid choice `{args.action}`, choose from {ACTIONS}")

    if args.action == "init":
        if args.project_name is None:
            logger.error("Action `init` requires project name")
        else:
            try:
                _validate_project_name(args.project_name)
            except ValueError as e:
                logger.error(str(e))

    if args.license not in LICENSES and args.license is not None:
        logger.error(f"Invalid choice `{args.license}`, choose from {ALLOWED_LICENSES}")


def main():
    parser = get_parser()
    args = parser.parse_args()

    options = {"quiet": args.quiet}

    # set up the console for logging
    logging_level = Level.INFO
    if options["quiet"]:
        logging_level = Level.ERROR
    logger = Logger(logging_level)

    _validate_input(args, logger)

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

    builder = ProjectBuilder(config=config, options=options, logger=logger)
    builder.dispatch(action=args.action, project_name=args.project_name)


if __name__ == "__main__":
    main()
