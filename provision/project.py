from invoke import task

from . import common


@task
def install_tools(context):
    """Install cli dependencies, and tools needed to install requirements."""
    context.run("pip install setuptools pip pip-tools wheel poetry")


@task
def install_requirements(context):
    """Install local development requirements."""
    common.success("Install requirements with poetry")
    context.run("cd server && poetry install")
