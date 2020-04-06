#!/bin/sh

## Make sure we have superuser privileges
[ "$(id -u)" -eq 0 ] || exec sudo "$0" "$@"

# Clean
emerge -ca
# Purge
revdep-rebuild -i -- -av
eclean-dist -d
emaint -f all
# Check
check_packages.py
