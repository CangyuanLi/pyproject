# pyproject:
[![PyPI version](https://badge.fury.io/py/pyproject-generator.svg)](https://badge.fury.io/py/pyproject-generator)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyproject)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)


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

## Running

Simply run
```sh
pyproject init {project_name}
```

to create your project folder. It will automatically setup a package structure, virtual
environment, and install packages.

![](demo.gif)

The final project structure looks like

```sh
├── .github
│   └── workflows
│       └── tests.yml
├── .gitignore
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
│       └── py.typed
├── tests
│   └── test_myproject.py
└── tox.ini
```

**pyproject** also allows you to configure your author name, email, Github url,
PyPI username and password, and a list of default dependencies that you want to install.
Please note that your credentials are simply stored locally as plaintext.
If you do not wish to store them, you can simply pass them in manually
via the --pypi_username and --pypi_password flags. To configure, run

```sh
pyproject config --author="" --email="" --github_url="" --pypi_username="" --pypi_password=""
```

You may set dependencies one of three ways. In all cases, pass in a comma-delimited string.
You can set the dependencies, which overrides the default settings.

```sh
pyproject config --set_dependencies
```

You may add dependencies:

```sh
pyproject config --add_dependencies
```

And you may remove dependencies:

```sh
pyproject config --remove_dependencies
```

**pyproject** also supplies an upload function. Run

```sh
pyproject upload
```

to build and upload your package to PyPI.
