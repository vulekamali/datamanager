#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


python manage.py collectstatic --noinput
gunicorn $GUNICORN_WORKERS_ARG --worker-class gevent budgetportal.wsgi:application --log-file - --bind 0.0.0.0:$PORT
