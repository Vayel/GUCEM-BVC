#!/bin/sh

DIR=$(cd "$(dirname "$0")" && pwd)

cd "$DIR/tools"
. ./work_in_env.sh

cd ..

echo ""
echo "================="
echo "Deployment checks"
echo "================="
./manage.py check --deploy

echo ""
echo "=========="
echo "Test mails"
echo "=========="

./manage.py test_mail

echo ""
echo "=========="
echo "Run server"
echo "=========="

./manage.py runmodwsgi "$@"
