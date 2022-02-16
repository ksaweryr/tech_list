#!/bin/sh

source venv/bin/activate

sqlite3 db.sqlite3 < schema.sql
python3 setup
