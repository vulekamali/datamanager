"""
Required arguments:

 - financial_year
 - sphere
 - filename

Required columns:

 - government
 - department_name

and either 'url' or 'path'

"""
from django.core.management.base import BaseCommand
from budgetportal.models import Department
import csv
import urllib
from tempfile import mkdtemp
import os
import urlparse
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'upload department datasets'

    def add_arguments(self, parser):
        parser.add_argument('financial_year', type=str)
        parser.add_argument('sphere', type=str)
        parser.add_argument('filename', type=str)
        parser.add_argument('--overwrite', dest='overwrite', default=False, action='store_true')

    def handle(self, *args, **options):
        financial_year = options['financial_year']
        sphere = options['sphere']
        filename = options['filename']
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                department = Department.objects.get(
                    government__sphere__financial_year__slug=financial_year,
                    government__sphere__slug=sphere,
                    government__slug=slugify(row['government']),
                    name=row['department_name'],
                )
                if 'url' in row:
                    local_path = download_file(row['url'])
                else:
                    local_path = row['path']
                department.upload_resource(local_path, overwrite=options['overwrite'])


def download_file(url):
    tempdir = mkdtemp(prefix="budgetportal")
    print "Downloading %s" % url
    basename = os.path.basename(urlparse.urlparse(url).path)
    filename = os.path.join(tempdir, basename)
    return urllib.urlretrieve(url, filename)[0]
