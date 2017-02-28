#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

. ./bvc/bin/activate
../manage.py "$@"
deactivate
