from autoslug import AutoSlugField
from collections import OrderedDict
from django.conf import settings
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import models
from django.utils.text import slugify as django_slugify
from slugify import slugify as extended_slugify
from partial_index import PartialIndex
from pprint import pformat
import logging
import re
import requests
import urlparse
from os.path import splitext, basename
import shutil

logger = logging.getLogger(__name__)
ckan = settings.CKAN


OPENSPENDING_ACCOUNT_ID = 'b9d2af843f3a7ca223eea07fb608e62a'
prov_abbrev = {
    'Eastern Cape': 'EC',
    'Free State': 'FS',
    'Gauteng': 'GT',
    'KwaZulu-Natal': 'NL',
    'Limpopo': 'LP',
    'Mpumalanga': 'MP',
    'Northern Cape': 'NC',
    'North West': 'NW',
    'Western Cape': 'WC',
}


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

    def get_starting_year(self):
        return self.slug[:4]

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
        logger.info(
            "query %s\nto ckan returned %d results",
            pformat(query),
            len(response['results'])
        )
        for package in response['results']:
            yield Dataset.from_package(self, package)

    def get_budget_revenue(self):
        """
        Get revenue data for the financial year
        """
        url = 'https://data.vulekamali.gov.za' \
              '/api/3/action' \
              '/datastore_search_sql'

        dataset_id = {
            '2017-18': 'b59a852f-7ae1-4a60-a827-643b151e458f',
            '2016-17': '69b54066-00e0-4d7b-8b33-1ccbace5ba8e',
            '2015-16': 'c484cd2b-da4e-4e71-aca8-f23989d0f3e0',
        }

        if self.slug not in dataset_id:
            return []

        sql = '''
        SELECT category_two,SUM(amount) AS amount FROM "{}"
         WHERE "phase"='After tax proposals'
         GROUP BY "category_two" ORDER BY amount DESC
        '''.format(dataset_id[self.slug])

        params = {
            'sql': sql
        }
        revenue_result = requests.get(url, params=params)

        revenue_result.raise_for_status()
        revenue_data = revenue_result.json()['result']['records']
        return revenue_data

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
    _function_budgets = None

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

    def get_vote_primary_departments(self):
        return Department.objects.filter(government=self, is_vote_primary=True).all()

    def get_function_budgets(self):
        """
        get the budget totals for all the government functions
        """

        if self._function_budgets is not None:
            return self._function_budgets

        dataset_id = 'estimates-of-%s-expenditure-south-africa-%s' % (
            self.sphere.slug,
            self.sphere.financial_year.slug,
        )
        cube_url = ('https://openspending.org/api/3/cubes/'
                    '{}:{}/').format(OPENSPENDING_ACCOUNT_ID, dataset_id)
        model_url = cube_url + 'model/'
        model_result = requests.get(model_url)
        logger.info(
            "request to %s took %dms",
            model_url,
            model_result.elapsed.microseconds / 1000
        )
        if model_result.status_code == 404:
            logger.info("No budget API found for %r", self)
            return None
        model_result.raise_for_status()
        model = model_result.json()['model']
        if not 'functional_classification' in model['hierarchies']:
            return None
        function_dimension = model['hierarchies']['functional_classification']['levels'][0]
        date_dimension = model['hierarchies']['date']['levels'][0]
        department_dimension = model['hierarchies']['administrative_classification']['levels'][0]
        financial_year_start = self.sphere.financial_year.get_starting_year()
        vote_numbers = [str(d.vote_number)
                        for d in self.get_vote_primary_departments()]
        votes = '"%s"' % '";"'.join(vote_numbers)
        cuts = [
            date_dimension + '.financial_year:' + financial_year_start,
            department_dimension + '.vote_number:' + votes
        ]
        if self.sphere.slug == 'provincial':
            geo_dimension = model['hierarchies']['geo_source']['levels'][0]
            cuts.append(geo_dimension + '.government:"%s"' % self.name)
        params = {
            'cut': "|".join(cuts),
            'drilldown': "|".join([
                function_dimension + '.government_function',
            ]),
            'pagesize': 30
        }
        aggregate_url = cube_url + 'aggregate/'
        aggregate_result = requests.get(aggregate_url, params=params)
        logger.info(
            "request %s with query %r took %dms",
            aggregate_result.url,
            pformat(params),
            aggregate_result.elapsed.microseconds / 1000
        )
        aggregate_result.raise_for_status()
        functions = []
        for cell in aggregate_result.json()['cells']:
            functions.append({
                'name': cell[function_dimension + '.government_function'],
                'total_budget': cell['value.sum']
            })
        self._function_budgets = functions
        return self._function_budgets

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Department(models.Model):
    organisational_unit = 'department'
    government = models.ForeignKey(Government, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True, editable=True)
    vote_number = models.IntegerField()
    is_vote_primary = models.BooleanField(default=True)
    intro = models.TextField()
    _programme_budgets = None

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        if self.pk:
            self.treasury_datasets = self.get_treasury_datasets()
            self.old_name = self.name
            self.old_slug = self.slug

    class Meta:
        unique_together = (
            ('government', 'slug'),
            ('government', 'name'),
        )
        indexes = [
            PartialIndex(fields=['government', 'vote_number'],
                         unique=True,
                         where='is_vote_primary'),
        ]

        ordering = ['vote_number']

    def save(self, *args, **kwargs):
        if self.pk and self.old_name != self.name:
            self._update_datasets()
        super(Department, self).save(*args, **kwargs)

    def clean(self):
        # This is only for user feedback in admin.
        # The constraint must be enforced elsewhere.
        existing_vote_primary = Department.objects.filter(
            government=self.government, vote_number=self.vote_number)
        if self.is_vote_primary and existing_vote_primary \
           and existing_vote_primary.first() != self:
            raise ValidationError('There is already a primary department for '
                                  'vote %d' % self.vote_number)

    def _update_datasets(self):
        if len(self.name) > 5 and self.is_vote_primary:  # If it's a really short name we can break stuff
            for dataset in self.treasury_datasets:
                new_slug = django_slugify(self.name)
                dataset['title'] = dataset['title'].replace(self.old_name, self.name)
                dataset['name'] = dataset['name'].replace(self.slug, new_slug)
                extras_set(dataset['extras'], 'Department Name', self.name)
                extras_set(dataset['extras'], 'department_name', self.name)
                extras_set(dataset['extras'], 'department_name_slug', new_slug)
                logger.info("Updating package %s with new name", dataset['id'])
                ckan.action.package_update(**dataset)
                for resource in dataset['resources']:
                    resource['name'] = resource['name'].replace(self.old_name, self.name)
                    logger.info("Updating resource %s with new name", resource['id'])
                    ckan.action.resource_update(**resource)
        else:
            logger.warn("Not updating datasets for %s", self.get_url_path())

    def _create_treasury_dataset(self):
        vocab_map = {}
        for vocab in ckan.action.vocabulary_list():
            vocab_map[vocab['name']] = vocab['id']
        dataset_fields = {
            'title': package_title(self),
            'name': package_id(self),
            'extras': [],
            'owner_org': 'national-treasury',
            'license_id': 'other-pd',
            'tags': [
                { 'vocabulary_id': vocab_map['spheres'],
                  'name': self.government.sphere.name },
                { 'vocabulary_id': vocab_map['financial_years'],
                  'name': self.get_financial_year().slug },
            ],
        }
        extras_set(dataset_fields['extras'], 'Department Name', self.name)
        extras_set(dataset_fields['extras'], 'department_name', self.name)
        extras_set(dataset_fields['extras'], 'department_name_slug', self.slug)
        extras_set(dataset_fields['extras'], 'Vote Number', self.vote_number)
        extras_set(dataset_fields['extras'], 'vote_number', self.vote_number)
        extras_set(dataset_fields['extras'], 'geographic_region_slug', self.government.slug)
        extras_set(dataset_fields['extras'], 'organisational_unit', 'department')
        ckan.action.package_create(**dataset_fields)

    def upload_resource(self, local_path):
        if not self.treasury_datasets:
            self._create_treasury_dataset()
        self.treasury_datasets = self.get_treasury_datasets()
        assert(len(self.treasury_datasets) == 1)
        dataset = self.treasury_datasets[0]
        resource = None
        for existing_resource in dataset['resources']:
            existing_path = urlparse.urlparse(existing_resource['url']).path
            existing_ext = splitext(basename(existing_path))[1]
            ext = splitext(local_path)[1]
            if existing_ext == ext:
                resource = existing_resource
        resource_fields = {
            'package_id': pid,
            'name': name,
            'upload': open(local_path, 'rb')
        }
        if resource:
            resource_fields['id'] = resource['id']
            result = ckan.action.resource_patch(**resource_fields)
        else:
            result = ckan.action.resource_create(**resource_fields)
        logger.info("Uploading resource result: %r", result)

    def get_url_path(self):
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)

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

    def get_primary_department(self):
        """
        Check if department is primary
        """
        if not self.is_vote_primary:
            try:
                dept = Department\
                       .objects \
                       .get(vote_number=self.vote_number,
                            is_vote_primary=True,
                            government=self.government)
            except MultipleObjectsReturned:
                logger.exception("Department %s has multiple primary "
                                 "departments" % self.slug)
                raise
            else:
                return dept
        return self

    def get_treasury_datasets(self):
        query = {
            'q': '',
            'fq': ('+organization:"national-treasury"'
                   '+vocab_financial_years:"%s"'
                   '+vocab_spheres:"%s"'
                   '+extras_s_geographic_region_slug:"%s"'
                   '+extras_s_department_name_slug:"%s"') % (
                       self.government.sphere.financial_year.slug,
                       self.government.sphere.slug,
                       self.government.slug,
                       self.get_primary_department().slug,
                   ),
            'rows': 1,
        }
        response = ckan.action.package_search(**query)
        logger.info(
            "query %s\nreturned %d results",
            pformat(query),
            len(response['results'])
        )
        return response['results']

    def get_treasury_resources(self):
        resources = {}
        datasets = self.get_treasury_datasets()
        if datasets:
            package = datasets[0]
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
            logger.info(
                "query %s\nto ckan returned %d results",
                pformat(params),
                len(response['results']))
            for package in response['results']:
                if package['name'] not in datasets:
                    dataset = Dataset.from_package(self.get_financial_year(), package)
                    datasets[package['name']] = dataset
        return datasets.values()

    def get_programme_budgets(self):
        """
        get the budget totals for all the department programmes
        """

        if self._programme_budgets is not None:
            return self._programme_budgets

        dataset_id = 'estimates-of-%s-expenditure-south-africa-%s' % (
            self.government.sphere.slug,
            self.get_financial_year().slug,
        )
        cube_url = ('https://openspending.org/api/3/cubes/'
                    '{}:{}/').format(OPENSPENDING_ACCOUNT_ID, dataset_id)
        model_url = cube_url + 'model/'
        model_result = requests.get(model_url)
        logger.info(
            "request to %s took %dms",
            model_url,
            model_result.elapsed.microseconds / 1000
        )
        if model_result.status_code == 404:
            return None
        model_result.raise_for_status()
        model = model_result.json()['model']
        programme_dimension = model['hierarchies']['activity']['levels'][0]
        financial_year_start = self.get_financial_year().get_starting_year()
        cuts = [
            'date_2.financial_year:' + financial_year_start,
            'administrative_classification_2.department:"' + self.name + '"'
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append('geo_source_2.government:"%s"' % self.government.name)
        params = {
            'cut': "|".join(cuts),
            'drilldown': "|".join([
                programme_dimension + '.programme_number',
                programme_dimension + '.programme',
            ]),
            'pagesize': 30
        }
        aggregate_url = cube_url + 'aggregate/'
        aggregate_result = requests.get(aggregate_url, params=params)
        logger.info(
            "request %s with query %r took %dms",
            aggregate_result.url,
            pformat(params),
            aggregate_result.elapsed.microseconds / 1000
        )
        aggregate_result.raise_for_status()
        programmes = []
        for cell in aggregate_result.json()['cells']:
            programmes.append({
                'name': cell[programme_dimension + '.programme'],
                'total_budget': cell['value.sum']
            })
        self._programme_budgets = programmes
        return self._programme_budgets

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

# https://stackoverflow.com/questions/35633037/search-for-document-in-solr-where-a-multivalue-field-is-either-empty-or-has-a-sp
def none_selected_query(vocab_name):
    """Match items where none of the options in a custom vocab tag is selected"""
    return '+(*:* NOT %s:["" TO *])' % vocab_name


def extras_set(extras, key, value):
    for extra in extras:
        if extra['key'] == key:
            extra['value'] = value
            break


def package_id(department):
    financial_year = department.get_financial_year()
    sphere = department.government.sphere
    geo_region = department.government.name
    if sphere.slug == 'provincial':
        short_dept = extended_slugify(department.name, max_length=85, word_boundary=True)
        return extended_slugify('prov dept %s %s %s' % (
            prov_abbrev[geo_region], short_dept, financial_year))
    elif sphere.slug == 'national':
        short_dept = extended_slugify(department.name, max_length=96, word_boundary=True)
        return extended_slugify('nat dept %s %s' % (short_dept, financial_year))
    else:
        raise Exception('unknown sphere %r' % sphere)


def package_title(department):
    financial_year = department.get_financial_year()
    sphere = department.government.sphere
    geo_region = department.government.name
    if sphere.slug == 'provincial':
        return "%s Department: %s %s" % (geo_region, department.name, financial_year)
    elif sphere.slug == 'national':
        return "National Department: %s %s" % (department.name, financial_year)
    else:
        raise Exception('unknown sphere %r' % sphere)
