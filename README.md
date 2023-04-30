# pyproject: 
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyproject)

## What is it?

**pyproject** is a command line utility to setup and distribute Python packages.

# Usage:

## Dependencies

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
