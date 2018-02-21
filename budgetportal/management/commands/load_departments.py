from django.core.management.base import BaseCommand
from budgetportal.models import Department, Government
import csv
from django.utils.text import slugify
import re


class Command(BaseCommand):
    help = 'load departments'

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
            government = Government.objects.get(
                sphere__financial_year__slug=financial_year,
                sphere__slug=sphere,
                slug=government,
            )
            reader = csv.DictReader(csvfile)
            for row in reader:
                intro = ""
                if row['purpose']:
                    intro += "## Vote purpose\n\n%s\n\n" % row['purpose']
                if row['mandate']:
                    intro += "## Mandate\n\n%s\n\n" % row['mandate']
                Department.objects.create(
                    government=government,
                    name=row['department_name'],
                    vote_number=row['vote_number'],
                    is_vote_primary=row['is_vote_primary'].upper() == 'TRUE',
                    intro=intro
                )
