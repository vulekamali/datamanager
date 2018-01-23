from django.core.management.base import BaseCommand
from budgetportal.models import Department, Programme
import csv
from django.utils.text import slugify
import re


class Command(BaseCommand):
    help = 'load programmes'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        with open(options['filename']) as csvfile:
            with open('missing_departments.csv', 'w') as missing_departments_file:
                reader = csv.DictReader(csvfile)
                missing_departments = None
                for row in reader:
                    if not missing_departments:
                        missing_departments = csv.DictWriter(missing_departments_file, reader.fieldnames)
                        missing_departments.writeheader()

                    departments = Department.objects.filter(
                        slug=slugify(row['Department']),
                        government__slug=slugify(row['government']),
                        government__sphere__slug=row['sphere'],
                        government__sphere__financial_year__slug=row['financial_year'],
                    )
                    if departments.count():
                        department = departments.first()
                        programme_name = row['Programme']
                        if not re.search('[a-z]', programme_name):
                            programme_name = programme_name.title()
                        Programme.objects.get_or_create(
                            name=programme_name,
                            slug=slugify(row['Programme']),
                            department=department,
                            programme_number=row['Programme No.'],
                        )
                    else:
                        missing_departments.writerow(row)
