# Gentoo scripts

[![pre-commit](https://github.com/KSmanis/gentoo-scripts/workflows/pre-commit/badge.svg)](https://github.com/KSmanis/gentoo-scripts/actions?workflow=pre-commit)
[![super-linter](https://github.com/KSmanis/gentoo-scripts/workflows/super-linter/badge.svg)](https://github.com/KSmanis/gentoo-scripts/actions?workflow=super-linter)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Maintenance scripts for Gentoo installations.

## Update scripts

Maintaining an up-to-date Gentoo installation can be achieved by invoking the
following scripts in order:

- [`update.sh`](update.sh) synchronizes all repositories.
- [`upgrade.sh`](upgrade.sh) upgrades all packages.
- [`clean.sh`](clean.sh) performs various cleanup operations.

### Auxiliary scripts

- [`check_packages.py`](check_packages.py) is used by the [`clean.sh`](clean.sh)
  script in order to check for obsolete package configuration (e.g., keywords and
  USE flags).
