from autoslug import AutoSlugField
from collections import OrderedDict
from django.conf import settings
from django.db import models
from requests.exceptions import HTTPError, ConnectionError
import logging
import re
import requests

logger = logging.getLogger(__name__)
ckan = settings.CKAN


class FinancialYear(models.Model):
    organisational_unit = 'financial_year'
    slug = models.SlugField(max_length=7, unique=True)

    @property
    def national(self):
        return self.spheres.filter(slug='national')[0]

    @property
    def provincial(self):
        return self.spheres.filter(slug='provincial')[0]

    def get_url_path(self):
        return "/%s" % self.slug

    def get_sphere(self, name):
        return getattr(self, name)

    def get_closest_match(self, department):
        sphere = self.spheres.filter(slug=department.government.sphere.slug).first()
        government = sphere.governments.filter(slug=department.government.slug).first()
        department = government.departments.filter(slug=department.slug).first()
        if not department:
            return government, False
        return department, True

    def get_contributed_datasets(self):
        query = {
            'q': '',
            'fq': '-organization:"national-treasury"',
            'rows': 1000,
        }
        response = ckan.action.package_search(**query)
        logger.info("query %r returned %d results", query, len(response['results']))
        for package in response['results']:
            yield Dataset.from_package(self, package)


    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Sphere(models.Model):
    organisational_unit = 'sphere'
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True)
    financial_year = models.ForeignKey(
        FinancialYear,
        on_delete=models.CASCADE,
        related_name="spheres",
    )

    class Meta:
        unique_together = (
            ('financial_year', 'slug'),
            ('financial_year', 'name'),
        )

    def get_url_path(self):
        return "%s/%s" % (self.financial_year.get_url_path(), self.slug)

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Government(models.Model):
    organisational_unit = 'government'
    sphere = models.ForeignKey(Sphere, on_delete=models.CASCADE, related_name="governments")
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True)

    class Meta:
        unique_together = (
            ('sphere', 'slug'),
            ('sphere', 'name'),
        )

    def get_url_path(self):
        if self.sphere.slug == 'national':
            return self.sphere.get_url_path()
        else:
            return "%s/%s" % (self.sphere.get_url_path(), self.slug)

    def get_department_by_slug(self, slug):
        departments = self.departments.objects.filter(slug=slug)
        if departments.count() == 0:
            return None
        elif departments.count() == 1:
            return departments.first()
        else:
            raise Exception("More matching slugs than expected")

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Department(models.Model):
    organisational_unit = 'department'
    government = models.ForeignKey(Government, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True, editable=True)
    vote_number = models.IntegerField()
    intro = models.TextField()

    class Meta:
        unique_together = (
            ('government', 'slug'),
            ('government', 'name'),
            ('government', 'vote_number'),
        )

        ordering = ['vote_number']

    def get_url_path(self):
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)

    def get_treasury_datasets(self):
        resources = {}

        query = {
            'q': '',
            'fq': ('+organization:"national-treasury"'
                   '+vocab_financial_years:"%s"'
                   '+vocab_spheres:"%s"'
                   '+extras_geographic_region_slug:"%s"'
                   '+extras_department_name_slug:"%s"') % (
                       self.government.sphere.financial_year.slug,
                       self.government.sphere.slug,
                       self.government.slug,
                       self.slug,
                   ),
            'rows': 1,
        }
        response = ckan.action.package_search(**query)
        logger.info("query %r returned %d results", query, len(response['results']))
        if response['results']:
            package = response['results'][0]
            for resource in package['resources']:
                if resource['name'].startswith('Vote'):
                    if self.government.sphere.slug == 'provincial':
                        doc_short = "EPRE"
                        doc_long = "Estimates of Provincial Revenue and Expenditure"
                    elif self.government.sphere.slug == 'national':
                        doc_short = "ENE"
                        doc_long = "Estimates of National Expenditure"
                    else:
                        raise Exception("unexpected sphere")
                    name = "%s for %s" % (doc_short, resource['name'])
                    description = ("The %s (%s) sets out the detailed spending "
                                   "plans of each government department for the "
                                   "coming year.") % (doc_long, doc_short)
                    if name not in resources:
                        resources[name] = {
                            'description': description,
                            'formats': [],
                        }
                    resources[name]['formats'].append({
                        'url': resource['url'],
                        'format': resource['format'],
                    })
        return resources

    def get_govt_functions(self):
        return GovtFunction.objects.filter(programme__department=self).distinct()

    def get_financial_year(self):
        return self.government.sphere.financial_year

    def _get_financial_year_query(self):
        return '+vocab_financial_years:"%s"' % self.get_financial_year().slug

    def _get_government_query(self):
        if self.government.sphere.slug == 'provincial':
            return '+vocab_provinces:"%s"' % self.government.name
        else:
            return none_selected_query('vocab_provinces')

    def _get_functions_query(self):
        function_names = [f.name for f in self.get_govt_functions()]
        ckan_tag_names = [re.sub('[^\w -]', '', n) for n in function_names]
        if len(ckan_tag_names) == 0:
            # We select datasets with no functions rather than datasets
            # with any function (e.g. a blank query) because this query
            # is intended to restrict datasets to matching functions.
            return none_selected_query('vocab_functions')
        else:
            options = ['+vocab_functions:"%s"' % n for n in ckan_tag_names]
            return '+(%s)' % ' OR '.join(options)

    def get_contributed_datasets(self):
        # We use an OrderedDict like an Ordered Set to ensure we include each
        # match just once, and at the highest rank it came up in.
        datasets = OrderedDict()

        fq_org = '-organization:"national-treasury"'
        fq_year = self._get_financial_year_query()
        fq_sphere = '+vocab_spheres:"%s"' % self.government.sphere.slug
        fq_government = self._get_government_query()
        fq_functions = self._get_functions_query()
        fq_no_functions = none_selected_query('vocab_functions')
        queries = [
            (fq_org, fq_year, fq_sphere, fq_government, fq_functions),
            (fq_org, fq_sphere, fq_government, fq_functions),
            (fq_org, fq_year, fq_sphere, fq_functions),
            (fq_org, fq_sphere, fq_functions),
            (fq_org, fq_functions),
            (fq_org, fq_no_functions),
        ]
        for query in queries:
            params = {
                'q': '',
                'fq': "".join(query),
                'rows': 1000,
            }
            response = ckan.action.package_search(**params)
            logger.info("query %r returned %d results", params, len(response['results']))
            for package in response['results']:
                if package['name'] not in datasets:
                    dataset = Dataset.from_package(self.get_financial_year(), package)
                    datasets[package['name']] = dataset
        return datasets.values()

    def get_budget_totals(self, year):
        """
        get the budget totals for all the department programmes
        """
        resource = {
            '2015': 'estimates-of-national-expenditure-south-africa-2015-16/',
            '2016': 'estimates-of-national-expenditure-south-africa-2016-17/',
            '2017': 'estimates-of-national-expenditure-south-africa-2017-18/'
        }
        params = {
            'cut': ('date_2.financial_year:{}|'
                    'administrative_classification_2.department:"{}"')
            .format(year.slug[:4], self.name),
            'drilldown': ('activity_programme_number.programme_number|'
                          'activity_programme_number.programme'),
            'order': 'activity_programme_number.programme_number:asc',
            'pagesize': 30
        }
        url = ('https://openspending.org/api/3/cubes/'
               'fb2fa9b200eb3e56facc4c287002fc4d:{}'
               'aggregate/').format(resource[year.slug[:4]])
        try:
            result = requests.get(url, params=params)
            if result.status_code == 200:
                if result.json()['status'] == 'ok':
                    return result.json()
        except (HTTPError, ConnectionError) as e:
            return None
        return None

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class GovtFunction(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True, unique=True)

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.slug)


class Programme(models.Model):
    organisational_unit = 'programme'
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programmes")
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True)
    programme_number = models.IntegerField()
    govt_functions = models.ManyToManyField(GovtFunction)

    class Meta:
        unique_together = (
            ('department', 'slug'),
            ('department', 'name'),
            ('department', 'programme_number'),
        )

        ordering = ['programme_number']

    def get_url_path(self):
        return "%s/programmes/%s" % (self.department.get_url_path(), self.slug)

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Dataset():
    def __init__(self, **kwargs):
        self.author = kwargs['author']
        self.created_date = kwargs['created_date']
        self.financial_year = kwargs['financial_year']
        self.last_updated_date = kwargs['last_updated_date']
        self.license = kwargs['license']
        self.name = kwargs['name']
        self.resources = kwargs['resources']
        self.slug = kwargs['slug']
        self.intro = kwargs['intro']
        self.methodology = kwargs['methodology']
        self.organization_slug = kwargs['organization_slug']

    @classmethod
    def from_package(cls, financial_year, package):
        resources = []
        for resource in package['resources']:
            resources.append({
                'name': resource['name'],
                'description': resource['description'],
                'format': resource['format'],
                'url': resource['url'],
            })
        return cls(
            financial_year=financial_year,
            slug=package['name'],
            name=package['title'],
            created_date=package['metadata_created'],
            last_updated_date=package['metadata_modified'],
            author={
                'name': package['author'],
                'email': package['author_email'],
            },
            license={
                'name': package['license_title'],
                'url': package['license_url'] if 'license_url' in package else None,
            },
            intro=package['notes'] if package['notes'] else None,
            methodology=package['methodology'] if 'methodology' in package else None,
            resources=resources,
            organization_slug=package['organization']['name'],
        )

    @classmethod
    def fetch(cls, financial_year, dataset_slug):
        package = ckan.action.package_show(id=dataset_slug)
        return cls.from_package(financial_year, package)

    def get_url_path(self):
        return "%s/datasets/%s" % (self.financial_year.get_url_path(), self.slug)

    def get_organization(self):
        org = ckan.action.organization_show(id=self.organization_slug)
        return {
            'name': org['title'],
            'logo_url': org['image_display_url'],
            'slug': org['name'],
            'url': org['url'] if 'url' in org else None,
            'telephone': org['telephone'] if 'telephone' in org else None,
            'email': org['email'] if 'email' in org else None,
            'facebook': org['facebook_id'] if 'facebook_id' in org else None,
            'twitter': org['twitter_id'] if 'twitter_id' in org else None,
        }


        # def get_related(self):
        # url: "2017-18/national/departments/health"
        # label: "National Department: Health"
        #return []

# https://stackoverflow.com/questions/35633037/search-for-document-in-solr-where-a-multivalue-field-is-either-empty-or-has-a-sp
def none_selected_query(vocab_name):
    """Match items where none of the options in a custom vocab tag is selected"""
    return '+(*:* NOT %s:["" TO *])' % vocab_name
