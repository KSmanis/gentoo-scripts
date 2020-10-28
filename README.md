# Gentoo scripts
[![lint](https://github.com/KSmanis/gentoo-scripts/workflows/lint/badge.svg)](https://github.com/KSmanis/gentoo-scripts/actions?workflow=lint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Maintenance scripts for Gentoo installations.

## Update scripts
Maintaining an up-to-date Gentoo installation can be achieved by invoking the following scripts in order:
* [`update.sh`](update.sh) synchronizes all repositories.
* [`upgrade.sh`](upgrade.sh) upgrades all packages.
* [`clean.sh`](clean.sh) performs various cleanup operations.

### Auxiliary scripts
* [`check_packages.py`](check_packages.py) is used by the [`clean.sh`](clean.sh) script in order to check for obsolete package configuration (e.g., keywords and USE flags).
