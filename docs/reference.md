# Reference

- Tools
  - Formatting
    - [Ruff][ruff] <sup>[config][pyproject_toml]</sup>
  - Linting
    - [Ruff][ruff] <sup>[config][pyproject_toml]</sup>
  - Automating
    - [pre-commit][pre-commit] <sup>[config][_pre-commit-config_yaml]</sup>
      <details>
        <summary>Hooks</summary>

        - [`ruff`][ruff]
        - [`poetry`][poetry]
          - `poetry-check`
          - `poetry-lock`
        - [`pre-commit-hooks`][pre-commit-hooks]
          - `check-toml`
          - `check-yaml`
          - `end-of-file-fixer`
          - `trailing-whitespace`
          - `requirements-txt-fixer`
      </details>
    - [Semantic Pull Requests][semantic-pull-requests]
    - [semantic-release][semantic-release] (used indirectly)
      - [python-semantic-release][python-semantic-release] <sup>[config][pyproject_toml]</sup>
    - [Codecov][codecov]
      - [Action][codecov-action]
      - [pyjop][codecov-project]
    - [Nox][nox] <sup>[config][noxfile_py]</sup>
    - [Cookiecutter][cookiecutter]
    - [cruft][cruft] <sup>[config][pyproject_toml]</sup>
  - Type checking
    - [Mypy][mypy] <sup>[config][pyproject_toml]</sup>
      - [Mypy Extensions][mypy-extensions]
  - Testing
    - [pytest][pytest] <sup>[config][pyproject_toml]</sup>
      - Plugins
        - [pytest-cov][pytest-cov]
        - [pytest-benchmark][pytest-benchmark]
    - [airspeed velocity (`asv`)][asv]
    - [Coverage.py][coveragepy] <sup>[config][pyproject_toml]</sup>
  - Documenting
    - [Sphinx][sphinx] <sup>[config][docs_conf_py]</sup>
      - [Furo][furo]
      - [sphinxcontrib-spelling][sphinxcontrib-spelling]
      - [MyST][myst]
    - [Google style docstrings][docstring_google]
  - Building
    - [Poetry][poetry]
      - [`pyproject.toml`][pyproject_toml]
  - Configuration Files
    - [`pyproject.toml`][pyproject_toml]
    - [`.pre-commit-config.yaml`][_pre-commit-config_yaml]
    - [`.editorconfig`][_editorconfig]
    - [`docs/conf.py`][docs_conf_py]
    - [`docs/wordlist.txt`][docs_wordlist_txt]
    - [`noxfile.py`][noxfile_py]
- Standards
  - Commits
    - [Conventional Commits][conventionalcommits]
  - Versioning
    - [Semantic Versioning][semver]
  - Contributing
    - [All Contributors][allcontributors]
  - [.gitignore][gitignore_python]
- Editor
  - [EditorConfig][editorconfig] <sup>[config][_editorconfig]</sup>
- Guidelines
  - [Angular `CONTRIBUTING.md`][angular-contributing]
  - [Contributor Covenant][contributor-covenant]
- Workflows
  - https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow
  - https://nvie.com/posts/a-successful-git-branching-model
  - https://github.community/t/syncing-a-fork-leaves-me-one-commit-ahead-of-upstream-master/1435/5
- Articles
  - [Don't commit `.vscode`][no-editor-config-gitignore]

[codecov-project]: https://app.codecov.io/gh/maschere/pyjop

[_pre-commit-config_yaml]: ../.pre-commit-config.yaml
[pyproject_toml]: ../pyproject.toml
[_editorconfig]: ../.editorconfig
[docs_conf_py]: ./conf.py
[docs_wordlist_txt]: ./wordlist.txt
[noxfile_py]: ../noxfile.py

[ruff]: https://github.com/astral-sh/ruff
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-hooks]: https://github.com/pre-commit/pre-commit-hooks
[rstcheck]: https://github.com/myint/rstcheck
[semantic-pull-requests]: https://github.com/zeke/semantic-pull-requests
[semantic-release]: https://github.com/semantic-release/semantic-release
[python-semantic-release]: https://github.com/relekang/python-semantic-release
[codecov]: https://codecov.io
[codecov-action]: https://github.com/marketplace/actions/codecov
[mypy]: https://github.com/python/mypy
[mypy-extensions]: https://github.com/python/mypy_extensions
[pytest]: https://github.com/pytest-dev/pytest
[pytest-cov]: https://github.com/pytest-dev/pytest-cov
[pytest-benchmark]: https://github.com/ionelmc/pytest-benchmark
[asv]: https://github.com/airspeed-velocity/asv
[coveragepy]: https://github.com/nedbat/coveragepy
[nox]: https://github.com/wntrblm/nox
[cruft]: https://github.com/cruft/cruft/
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[sphinx]: https://www.sphinx-doc.org
[furo]: https://github.com/pradyunsg/furo
[sphinxcontrib-spelling]: https://github.com/sphinx-contrib/spelling
[myst]: https://github.com/executablebooks/myst-parser
[docstring_google]: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
[poetry]: https://python-poetry.org
[conventionalcommits]: https://www.conventionalcommits.org
[semver]: https://semver.org
[allcontributors]: https://github.com/all-contributors/all-contributors
[no-editor-config-gitignore]: https://blog.martinhujer.cz/dont-put-idea-vscode-directories-to-projects-gitignore
[editorconfig]: https://editorconfig.org
[angular-contributing]: https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit
[contributor-covenant]: https://contributor-covenant.org
[gitignore_python]: https://github.com/github/gitignore/blob/master/Python.gitignore
