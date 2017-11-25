#!/bin/sh

DIR="$(cd "$(dirname "$0")" ; pwd)"
cd "$DIR"

. ./work_in_env.sh
../manage.py "$@"
deactivate
