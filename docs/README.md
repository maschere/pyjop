<div align="center">

  [![Discord][badge-chat]][chat]
  <br>
  <br>

  | | ![Badges][label-badges] |
  |:-|:-|
  | ![Build][label-build] | [![Nox][badge-actions]][actions] [![semantic-release][badge-semantic-release]][semantic-release] [![PyPI][badge-pypi]][pypi] [![Read the Docs][badge-docs]][docs] |
  | ![Tests][label-tests] | [![coverage][badge-coverage]][coverage] [![pre-commit][badge-pre-commit]][pre-commit] [![asv][badge-asv]][asv] |
  | ![Standards][label-standards] | [![SemVer 2.0.0][badge-semver]][semver] [![Conventional Commits][badge-conventional-commits]][conventional-commits] |
  | ![Code][label-code] | [![Poetry][badge-poetry]][poetry] [![Ruff][badge-ruff]][ruff] [![Checked with mypy][badge-mypy]][mypy] |
  | ![Repo][label-repo] | [![GitHub issues][badge-issues]][issues] [![GitHub stars][badge-stars]][stars] [![GitHub license][badge-license]][license] [![All Contributors][badge-all-contributors]][contributors] [![Contributor Covenant][badge-code-of-conduct]][code-of-conduct] |
</div>

<!-- Badges -->
[badge-chat]: https://img.shields.io/badge/dynamic/json?color=green&label=chat&query=%24.approximate_presence_count&suffix=%20online&logo=discord&style=flat-square&url=https%3A%2F%2Fdiscord.com%2Fapi%2Fv10%2Finvites%2F2ZrdzkNeBP%3Fwith_counts%3Dtrue
[chat]: https://discord.gg/2ZrdzkNeBP

<!-- Labels -->
[label-badges]: https://img.shields.io/badge/%F0%9F%94%96-badges-purple?style=for-the-badge
[label-build]: https://img.shields.io/badge/%F0%9F%94%A7-build-darkblue?style=flat-square
[label-tests]: https://img.shields.io/badge/%F0%9F%A7%AA-tests-darkblue?style=flat-square
[label-standards]: https://img.shields.io/badge/%F0%9F%93%91-standards-darkblue?style=flat-square
[label-code]: https://img.shields.io/badge/%F0%9F%92%BB-code-darkblue?style=flat-square
[label-repo]: https://img.shields.io/badge/%F0%9F%93%81-repo-darkblue?style=flat-square

<!-- Build -->
[badge-actions]: https://img.shields.io/github/actions/workflow/status/maschere/pyjop/ci.yml?branch=main&style=flat-square
[actions]: https://github.com/maschere/pyjop/actions
[badge-semantic-release]: https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079?style=flat-square
[semantic-release]: https://github.com/semantic-release/semantic-release
[badge-pypi]: https://img.shields.io/pypi/v/pyjop?style=flat-square
[pypi]: https://pypi.org/project/pyjop
[badge-docs]: https://img.shields.io/readthedocs/pyjop?style=flat-square
[docs]: https://pyjop.readthedocs.io

<!-- Tests -->
[badge-coverage]: https://img.shields.io/codecov/c/gh/maschere/pyjop?logo=codecov&style=flat-square
[coverage]: https://codecov.io/gh/maschere/pyjop
[badge-pre-commit]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white
[pre-commit]: https://github.com/pre-commit/pre-commit
[badge-asv]: https://img.shields.io/badge/benchmarked%20by-asv-blue?style=flat-square
[asv]: https://github.com/airspeed-velocity/asv

<!-- Standards -->
[badge-semver]: https://img.shields.io/badge/SemVer-2.0.0-blue?style=flat-square&logo=semver
[semver]: https://semver.org/spec/v2.0.0.html
[badge-conventional-commits]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow?style=flat-square
[conventional-commits]: https://conventionalcommits.org

<!-- Code -->
[badge-poetry]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json&style=flat-square
[poetry]: https://python-poetry.org
[badge-ruff]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square
[ruff]: https://github.com/astral-sh/ruff
[badge-mypy]: https://img.shields.io/badge/mypy-checked-2A6DB2?style=flat-square
[mypy]: http://mypy-lang.org

<!-- Repo -->
[badge-issues]: https://img.shields.io/github/issues/maschere/pyjop?style=flat-square
[issues]: https://github.com/maschere/pyjop/issues
[badge-stars]: https://img.shields.io/github/stars/maschere/pyjop?style=flat-square
[stars]: https://github.com/maschere/pyjop/stargazers
[badge-license]: https://img.shields.io/github/license/maschere/pyjop?style=flat-square
[license]: https://github.com/maschere/pyjop/blob/main/LICENSE
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[badge-all-contributors]: https://img.shields.io/badge/all_contributors-0-orange.svg?style=flat-square
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[contributors]: #Contributors-✨
[badge-code-of-conduct]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa?style=flat-square
[code-of-conduct]: CODE_OF_CONDUCT.md
<!---->

# pyjop
Official Python interface for JOY OF PROGRAMMING. More info about the game at https://store.steampowered.com/app/2216770

[Read the Docs][docs]

## Installation
pyjop comes pre-packaged with JOY OF PROGRAMMING in a dedicated Python env. So for the default gaming experience, a manual installation is not needed.
If you wish to use use your own Python interpreter and IDE to communicate with the game, please install pyjop and its requirements in the Python environment of your choice. Please note that this disables the sandboxing normally used within the game and also prevents some gameplay (features like unlocking certain modules) from working correctly. As such, this is not recommended for the normal gaming experience, but certainly has its uses beyond that.

### PyPI
[*pyjop*][pypi] is available on PyPI:

```bash
# With pip
pip install pyjop
# With Poetry
poetry add pyjop
```

### GitHub
You can also install the latest version of the code directly from GitHub:
```bash
# With pip
pip install git+git://github.com/maschere/pyjop
# With Poetry
poetry add git+git://github.com/maschere/pyjop
```

## Usage
For more examples, see the [full documentation][docs].

```python
from pyjop import *
```

## Contributing
If you wish to contribute to pyjop, please feel free to fork this repo and issue pull requests. Additionally please join our Discord server to discuss potential changes.

https://discord.com/invite/2ZrdzkNeBP

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

More details can be found in [CONTRIBUTING](CONTRIBUTING.md).

### Third-party programming interfaces
If you are interested in creating a differently flavored Python-wrapper for JOY OF PROGRAMMING or an interface for any other programming language, you are welcome to use this repo as reference. The most important part is re-implementing the socket communication protocol. See class [NPArray](https://github.com/maschere/pyjop/blob/main/pyjop/EntityBase.py#L46) as the starting point. Feel free to mention and discuss these projects on our Discord and I can also link to them from this section. Just let me know.

## Contributors ✨
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License
[MIT](../LICENSE)

This project was created with the [MicaelJarniac/crustypy](https://github.com/MicaelJarniac/crustypy) template.
