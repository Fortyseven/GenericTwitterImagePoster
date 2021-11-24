#!/usr/bin/env bash
set -e

DIR=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cd $DIR
. ./venv/bin/activate
python ./post-frame.py
cd - > /dev/null
