from django.core.management.base import BaseCommand
from budgetportal.models import GovtFunction, Programme
import csv
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'load functions'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        with open(options['filename']) as csvfile:
            with open('missing_programmes.csv', 'w') as missing_programmes:
                reader = csv.DictReader(csvfile)
                functions = GovtFunction.objects.all()
                functions_by_slug = {}
                for function in functions:
                    functions_by_slug[function.slug] = function

                for row in reader:
                    programmes = Programme.objects.filter(
                        slug=slugify(row['Programme']),
                        department__slug=slugify(row['Department']),
                        department__government__slug=slugify(row['Province']),
                    )
                    function = functions_by_slug[slugify(row['Function group'])]
                    if programmes.count():
                        for programme in programmes:
                            programme.govt_functions.add(function)
                            programme.save()
                    else:
                        missing_programmes.write("%r\n" % row)
