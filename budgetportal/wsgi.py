"""
WSGI config for budgetportal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

from psycogreen.gevent import patch_psycopg
import os

from django.core.wsgi import get_wsgi_application

from gevent import monkey
monkey.patch_all()

patch_psycopg()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "budgetportal.settings")

application = get_wsgi_application()
