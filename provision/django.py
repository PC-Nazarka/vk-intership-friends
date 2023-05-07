from invoke import task

from . import common, docker


@task
def manage(context, service="django", command="", compose="dev"):
    """Base template for commands with python manage.py."""
    docker.docker_compose_run(
        context,
        service,
        f"python manage.py {command}",
        compose,
    )


@task
def makemigrations(context, command=""):
    """Run makemigrations command and chown created migrations."""
    common.success("Django: Make migrations")
    manage(context, command=f"makemigrations {command}")


@task
def migrate(context, app_name=""):
    """Run ``migrate`` command."""
    common.success("Django: Apply migrations")
    manage(context, command=f"migrate {app_name}")


@task
def shell(context, params=""):
    """Shortcut for manage.py shell_plus command."""
    common.success("Entering Django Shell")
    manage(context, command=f"shell {params}")
