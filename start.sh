#!/bin/bash
set -euo pipefail

python manage.py wait_for_database
python manage.py migrate

if [ "${1:-prod}" = "dev" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  python manage.py collectstatic --no-input
  exec gunicorn trojstenid.wsgi --bind 0.0.0.0:8000 --access-logfile - --log-file -
fi
