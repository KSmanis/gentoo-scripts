# Gentoo scripts
Maintenance scripts for Gentoo installations.

## Update scripts
Maintaining an up-to-date Gentoo installation can be achieved by invoking the following scripts in order:
 * [`update`](update) synchronizes all repositories.
 * [`upgrade`](upgrade) upgrades all packages.
 * [`clean`](clean) performs various cleanup operations.

### Auxiliary scripts
 * [`check_packages.py`](check_packages.py) is used by the [`clean`](clean) script in order to check for obsolete package configuration (e.g., keywords and USE flags).
