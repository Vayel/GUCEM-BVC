#!/bin/sh

DIR=$(cd "$(dirname "$0")" && pwd)

. "$DIR/work_in_env.sh"

echo "Please make sure:"
echo "* the Django app is configured for production (https://docs.djangoproject.com/fr/1.10/howto/deployment/checklist/)"
echo "* all dependencies are installed (cf. the documentation of deployment)"
echo "Quit (Ctrl+C) if it is not the case, else press ENTER"
read x

echo ""
echo "=============================="
echo "Installing Python dependencies"
echo "=============================="
echo ""

pip install -r "$DIR"/../requirements.txt

echo ""
echo "====================="
echo "Creating the database"
echo "====================="
echo ""

"$DIR"/../manage.py makemigrations
"$DIR"/../manage.py migrate

echo ""
echo "=========================="
echo "Creating the admin account"
echo "=========================="
echo ""

echo "Can be skipped with Ctrl+C"
echo ""

"$DIR"/../manage.py createsuperuser

echo ""
echo "===================================="
echo "Creating the cron task for reminders"
echo "===================================="
echo ""

python "$DIR"/create_reminders_cron.py
python "$DIR"/create_transmit_grouped_command_cron.py

echo ""
echo "=========================================="
echo "Creating the cron task for database backup"
echo "=========================================="
echo ""

python "$DIR"/create_db_backup_cron.py

echo ""
echo "==================="
echo "Installing mod_wsgi"
echo "==================="
echo ""

pip install mod_wsgi

echo ""
echo "=============="
echo "TODO (for you)"
echo "=============="
echo ""

echo "* Configure mod_wsgi for Django (https://github.com/GrahamDumpleton/mod_wsgi#using-mod_wsgi-express-with-django)"
