#!/usr/bin/env sh
set -eu

root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
exec git --git-dir="$root/.repo.git" --work-tree="$root" "$@"
