#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

yarn build
python manage.py collectstatic --noinput
gunicorn --workers $GUNICORN_WORKERS_ARG --config gunicorn.config.py budgetportal.wsgi:application --log-file - --bind 0.0.0.0:$PORT
