#!/bin/sh

DIR=$(cd "$(dirname "$0")" && pwd)

cd "$DIR"

DUMP_FNAME=db_dump.sql
# We need the id of the file (not of the folder) for gdrive to create a new
# revision and not a new file
# To be specified manually at configuration
DRIVE_FILE_ID=""

sqlite3 "../db.sqlite3" <<EOF
.o $DUMP_FNAME
.dump
.exit
EOF

gdrive -c "$DIR" update $DRIVE_FILE_ID $DUMP_FNAME
