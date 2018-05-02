"""
Required arguments:

 - financial_year
 - sphere
 - filename

Required columns:

 - government
 - department_name
 - vote_number

Optional columns:

 - is_vote_primary
 - purpose
 - mandate
 - vision
 - mission
 - core_functions_and_responsibilities

"""
from django.core.management.base import BaseCommand
from budgetportal.models import Department, Government
import csv
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'load departments'

    def add_arguments(self, parser):
        parser.add_argument('financial_year', type=str)
        parser.add_argument('sphere', type=str)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        financial_year = options['financial_year']
        sphere = options['sphere']
        filename = options['filename']
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                government = Government.objects.get(
                    sphere__financial_year__slug=financial_year,
                    sphere__slug=sphere,
                    slug=slugify(row['government']),
                )
                intro = ""
                if row.get('purpose', False):
                    intro += "## Vote purpose\n\n%s\n\n" % row['purpose']
                if row.get('vision', False):
                    intro += "## Vision\n\n%s\n\n" % row['vision']
                if row.get('mission', False):
                    intro += "## Mission\n\n%s\n\n" % row['mission']
                if row.get('mandate', False):
                    intro += "## Mandate\n\n%s\n\n" % row['mandate']
                if row.get('core functions and responsibilities', False):
                    intro += "## Core functions and responsibilities\n\n%s\n\n" % row['core_functions_and_responsibilities']
                is_vote_primary = row.get('is_vote_primary', None)
                if is_vote_primary is None:
                    is_vote_primary = True
                else:
                    is_vote_primary = is_vote_primary.upper() == 'TRUE'
                Department.objects.create(
                    government=government,
                    name=row['department_name'],
                    vote_number=row['vote_number'],
                    is_vote_primary=is_vote_primary,
                    intro=intro
                )
