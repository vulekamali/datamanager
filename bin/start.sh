#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


python manage.py collectstatic --noinput
gunicorn $GUNICORN_WORKERS_ARG budgetportal.wsgi:application --log-file - --bind 0.0.0.0:$PORT
