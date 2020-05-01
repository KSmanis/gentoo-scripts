#!/bin/sh

## Make sure we have superuser privileges
[ "$(id -u)" -eq 0 ] || exec sudo "$0" "$@"

emaint sync --auto
