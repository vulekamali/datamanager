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
 - intro
 - website_url

"""
import csv

from budgetportal.models import Department, Government
from django.core.management.base import BaseCommand
from django.utils.text import slugify


class Command(BaseCommand):
    help = "load departments"

    def add_arguments(self, parser):
        parser.add_argument("financial_year", type=str)
        parser.add_argument("sphere", type=str)
        parser.add_argument("filename", type=str)
        parser.add_argument("update", type=bool, nargs="?", default=False)

    def handle(self, *args, **options):
        financial_year = options["financial_year"]
        sphere = options["sphere"]
        filename = options["filename"]
        update = options.get("update", False)

        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    government = Government.objects.get(
                        sphere__financial_year__slug=financial_year,
                        sphere__slug=sphere,
                        slug=slugify(row["government"]),
                    )
                except Government.DoesNotExist:
                    print(
                        "Missing government: {} {} {}".format(
                            financial_year, sphere, row["government"]
                        )
                    )
                    raise
                intro = ""
                website_url = None
                if row.get("intro", False):
                    intro += row["intro"]
                if row.get("website_url", False):
                    website_url = row["website_url"]
                is_vote_primary = row.get("is_vote_primary", None)
                if is_vote_primary is None:
                    is_vote_primary = True
                else:
                    is_vote_primary = is_vote_primary.upper() == "TRUE"

                def create_dept():
                    Department.objects.create(
                        government=government,
                        name=row["department_name"],
                        vote_number=row["vote_number"],
                        is_vote_primary=is_vote_primary,
                        intro=intro,
                        website_url=website_url,
                    )

                try:
                    if update:
                        department = Department.objects.get(
                            government=government, name=row["department_name"]
                        )
                        department.government = government
                        department.vote_number = row["vote_number"]
                        department.is_vote_primary = is_vote_primary
                        department.intro = intro
                        department.website_url = website_url
                        department.save()
                    else:
                        create_dept()
                except Department.DoesNotExist:
                    create_dept()
