from django.core.management.base import BaseCommand
from budgetportal.models import GovtFunction, Programme
import csv
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'load functions'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('financial_year', type=str)

    def handle(self, *args, **options):
        with open(options['filename']) as csvfile:
            with open('missing_programmes.csv', 'w') as missing_programmes_file:
                with open('missing_functions.csv', 'w') as missing_functions:
                    reader = csv.DictReader(csvfile)

                    # Set up function cache
                    functions = GovtFunction.objects.all()
                    functions_by_slug = {}
                    for function in functions:
                        functions_by_slug[function.slug] = function

                    # Set up missing programme CSV
                    missing_programmes = None
                    if not missing_programmes:
                        missing_programmes = csv.DictWriter(missing_programmes_file, reader.fieldnames)
                        missing_programmes.writeheader()

                    for row in reader:
                        programmes = Programme.objects.filter(
                            slug=slugify(row['Programme']),
                            department__slug=slugify(row['Department']),
                            department__government__slug=slugify(row['Government']),
                            department__government__sphere__financial_year__slug=options['financial_year'],
                        )
                        function_slug = slugify(row['Function group'])
                        if function_slug in functions_by_slug:
                            function = functions_by_slug[function_slug]
                            if programmes.count():
                                for programme in programmes:
                                    programme.govt_functions.add(function)
                                    programme.save()
                            else:
                                missing_programmes.writerow(row)
                        else:
                            missing_functions.write("%s\n" % function_slug)
