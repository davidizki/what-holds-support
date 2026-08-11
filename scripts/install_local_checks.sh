#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
git -C "$repo_dir" config core.hooksPath .githooks

echo "Installed the What Holds website pre-push check."
