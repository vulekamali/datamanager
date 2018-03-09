from django.core.management.base import BaseCommand
from budgetportal.models import Department
import csv
import urllib
from tempfile import mkdtemp
import os
import urlparse


class Command(BaseCommand):
    help = 'upload department datasets'

    def add_arguments(self, parser):
        parser.add_argument('financial_year', type=str)
        parser.add_argument('sphere', type=str)
        parser.add_argument('government', type=str)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        financial_year = options['financial_year']
        sphere = options['sphere']
        government = options['government']
        filename = options['filename']
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                department = Department.objects.get(
                    government__sphere__financial_year__slug=financial_year,
                    government__sphere__slug=sphere,
                    government__slug=government,
                    name=row['department_name'],
                )
                if row['url']:
                    local_path = download_file(row['url'])
                else:
                    local_path = row['path']
                department.upload_resource(local_path)


def download_file(url):
    tempdir = mkdtemp(prefix="budgetportal")
    print "Downloading %s" % url
    basename = os.path.basename(urlparse.urlparse(url).path)
    filename = os.path.join(tempdir, basename)
    return urllib.urlretrieve(url, filename)[0]
