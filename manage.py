#!/usr/bin/env python
from psycogreen.gevent import patch_psycopg
import os
import sys

from gevent import monkey

monkey.patch_all()

patch_psycopg()


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "budgetportal.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
