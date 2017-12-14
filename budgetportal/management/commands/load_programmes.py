from django.core.management.base import BaseCommand
from budgetportal.models import Department, Programme
import csv
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'load programmes'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        with open(options['filename']) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                department = Department.objects.get(
                    slug=slugify(row['Department']),
                    government__slug=slugify(row['government']),
                    government__sphere__slug=row['sphere'],
                    government__sphere__financial_year__slug=row['financial_year'],
                )
                Programme.objects.get_or_create(
                    name=row['Programme'],
                    slug=slugify(row['Programme']),
                    department=department
                )
