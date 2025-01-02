"""Nox file for automation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

import nox

python_versions = ["3.10", "3.11", "3.12", "3.13"]
venv_params = ["--no-setuptools", "--no-wheel"]


def install(
    session: nox.Session,
    *,
    groups: Iterable[str],
    root: bool = True,
    only: bool | None = None,
    extras: bool = False,
) -> None:
    """Install the dependency groups using Poetry."""
    if only is None:
        only = not root

    command = [
        "poetry",
        "install",
        "--sync",
        f'--{"only" if only else "with"}={",".join(groups)}',
    ]
    if not root:
        command.append("--no-root")
    if extras:
        command.append("--all-extras")

    session.run_always(*command, external=True)


@nox.session(python=python_versions[-1], venv_params=venv_params)
def pre_commit(session: nox.Session) -> None:
    """Run pre-commit."""
    install(session, groups=["pre-commit"], root=False)
    session.run(
        "pre-commit",
        "run",
        "--all-files",
        "--show-diff-on-failure",
        "--hook-stage=manual",
    )


@nox.session(python=python_versions[-1], venv_params=venv_params)
def lint_files(session: nox.Session) -> None:
    """Lint and fix files."""
    install(session, groups=["linting"], root=False)
    session.run("ruff", "check", ".", "--fix")


@nox.session(python=python_versions[-1], venv_params=venv_params)
def format_files(session: nox.Session) -> None:
    """Format files."""
    install(session, groups=["linting"], root=False)
    session.run("ruff", "format")


@nox.session(python=python_versions, venv_params=venv_params)
def type_check_code(session: nox.Session) -> None:
    """Type-check code."""
    install(
        session,
        groups=["main", "typing"],
        root=True,
        only=True,
        extras=True,
    )
    # mypy --install-types
    session.run("mypy")


@nox.session(python=python_versions, venv_params=venv_params)
def test_code(session: nox.Session) -> None:
    """Test code."""
    install(session, groups=["main", "tests"], root=True, only=True, extras=True)
    session.run("pytest")
