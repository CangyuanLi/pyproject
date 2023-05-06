# pyproject:
[![PyPI version](https://badge.fury.io/py/pyproject-generator.svg)](https://badge.fury.io/py/pyproject-generator)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyproject)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
![Tests](https://github.com/CangyuanLi/pyproject/actions/workflows/tests.yaml/badge.svg)
![Coverage](https://github.com/CangyuanLi/pyproject/blob/master/assets/coverage.svg)


## What is it?

**pyproject** is a command line utility to setup and distribute Python packages.

# Usage:

## Dependencies

- [platformdirs](https://pypi.org/project/platformdirs/) - Install configuration files in the correct location
- [rich](https://pypi.org/project/rich/) - Beautiful terminal output

## Installing

The easiest way is to install **pyproject** is from PyPI using pip:

```sh
pip install pyproject-generator
```

Afterwards, a pyproject command will be exposed on your system.

## Initializing a Project

Simply run
```sh
pyproject init {project_name}
```

to create your project folder. It will automatically setup a package structure, virtual
environment, and install packages.

![](https://raw.githubusercontent.com/CangyuanLi/pyproject/master/assets/demo.gif)

The final project structure looks like

```sh
├── .git
├── .github
│   └── workflows
│       └── tests.yml
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── benchmarks
│   └── benchmark.py
├── pyproject.toml
├── requirements_dev.txt
├── setup.cfg
├── src
│   └── myproject
│       ├── __init__.py
│       ├── __version__.py
│       └── py.typed
├── tests
│   └── test_myproject.py
└── tox.ini
```

## Configuring pyproject-generator

**pyproject** also allows you to configure your author name, email, Github URL,
PyPI username and password, and a list of default dependencies that you want to install.
Please note that your credentials are simply stored locally as plaintext.
If you do not wish to store them, you can simply pass them in manually
via the --pypi_username and --pypi_password flags, or run without any flags and type
them in as required. To configure, run

```sh
pyproject config --author="" --email="" --github_url="" --pypi_username="" --pypi_password=""
```

You may set dependencies one of three ways. In all cases, pass in a comma-delimited
string (for multiple dependencies) or a string (for one dependency).
You can set the dependencies, which overrides the default settings.

```sh
pyproject config --set_dependencies="white,ruff,mypy"
```

You may add dependencies:

```sh
pyproject config --add_dependencies="django"
```

And you may remove dependencies:

```sh
pyproject config --remove_dependencies="pre-commit"
```

Note that these flags also work with the `init` action. `config` merely does the work
of saving them locally to be re-used later.

## Uploading a Project

**pyproject** also supplies an upload function. Run

```sh
pyproject upload
```

to build and upload your package to PyPI.
