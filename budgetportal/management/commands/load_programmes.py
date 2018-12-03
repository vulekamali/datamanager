from django.core.management.base import BaseCommand
from budgetportal.models import Department, Programme
import csv
from django.utils.text import slugify
import re
import sys
import yaml

class Command(BaseCommand):
    help = ("Load Programmes. If a programme with that name for the department "
            "already exists, don't duplicate. If a department is missing, the "
            "programme's row will be written to missing_departments.csv")

    def add_arguments(self, parser):
        parser.add_argument('financial_year_slug', type=str)
        parser.add_argument('sphere_slug', type=str)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        financial_year = options['financial_year_slug']
        sphere = options['sphere_slug']
        filename = options['filename']
        number_added = 0
        number_missing_department = 0
        number_existing = 0

        with open(filename) as csvfile:
            with open('missing_departments.csv', 'w') as missing_departments_file:
                reader = csv.DictReader(csvfile)
                missing_departments = None
                for row in reader:
                    if not missing_departments:
                        # Initialise here so that header row of import has been read and is available
                        missing_departments = csv.DictWriter(missing_departments_file, reader.fieldnames)
                        missing_departments.writeheader()

                    departments = Department.objects.filter(
                        slug=slugify(row['department_name']),
                        government__slug=slugify(row['government_name']),
                        government__sphere__slug=sphere,
                        government__sphere__financial_year__slug=financial_year,
                    )
                    if departments.count():
                        department = departments.first()
                        programme_name = row['programme_name']
                        if not re.search('[a-z]', programme_name):
                            programme_name = programme_name.title()
                        obj, created = Programme.objects.get_or_create(
                            name=programme_name,
                            slug=slugify(row['programme_name']),
                            department=department,
                            programme_number=row['programme_number'],
                        )
                        if created:
                            number_added += 1
                        else:
                            number_existing += 1
                    else:
                        print "Couldn't find department for %r" % row
                        number_missing_department += 1
                        missing_departments.writerow(row)
        return yaml.dump({
            'number_added': number_added,
            'number_missing_department': number_missing_department,
            'number_existing': number_existing,
        }, default_flow_style=False)
