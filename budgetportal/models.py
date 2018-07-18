from autoslug import AutoSlugField
from collections import OrderedDict
from django.conf import settings
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import models
from django.utils.text import slugify as django_slugify
from slugify import slugify as extended_slugify
from partial_index import PartialIndex
from pprint import pformat
from budgetportal.openspending import EstimatesOfExpenditure
import logging
import re
import requests
import urlparse
from os.path import splitext, basename
from decimal import Decimal

logger = logging.getLogger(__name__)
ckan = settings.CKAN

CKAN_DATASTORE_URL = ('https://data.vulekamali.gov.za'
                      '/api/3/action' \
                      '/datastore_search_sql')

REVENUE_RESOURCE_IDS = {
    '2018-19': '7ad5e908-5814-4581-a9df-a6f37c56d5bd',
    '2017-18': 'b59a852f-7ae1-4a60-a827-643b151e458f',
    '2016-17': '69b54066-00e0-4d7b-8b33-1ccbace5ba8e',
    '2015-16': 'c484cd2b-da4e-4e71-aca8-f23989d0f3e0',
}


CPI_RESOURCE_IDS = {
    '2018-19': '5b315ff0-55e9-4ba8-b88c-2d70093bfe9d',
}

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

# Budget Phase IDs for the 7-year overview period
TRENDS_AND_ESTIMATES_PHASES = [
    'Audited Outcome',
    'Audited Outcome',
    'Audited Outcome',
    'Adjusted appropriation',
    'Main appropriation',
    'Medium Term Estimates',
    'Medium Term Estimates',
]


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

    @staticmethod
    def slug_from_year_start(year):
        return year + '-' + str(int(year[2:])+1)

    def get_sphere(self, name):
        return getattr(self, name)

    def get_closest_match(self, department):
        sphere = self.spheres.filter(slug=department.government.sphere.slug).first()
        government = sphere.governments.filter(slug=department.government.slug).first()
        department = government.departments.filter(slug=department.slug).first()
        if not department:
            return government, False
        return department, True

    def get_budget_revenue(self):
        """
        Get revenue data for the financial year
        """
        if self.slug not in REVENUE_RESOURCE_IDS:
            return []

        sql = '''
        SELECT category_two, SUM(amount) AS amount FROM "{}"
         WHERE "phase"='After tax proposals'
         GROUP BY "category_two" ORDER BY amount DESC
        '''.format(REVENUE_RESOURCE_IDS[self.slug])

        params = {
            'sql': sql
        }
        revenue_result = requests.get(CKAN_DATASTORE_URL, params=params)

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
        budget = EstimatesOfExpenditure(
            financial_year_slug=self.get_financial_year().slug,
            sphere_slug=self.government.sphere.slug,
        )
        financial_year_start = self.sphere.financial_year.get_starting_year()
        vote_numbers = [str(d.vote_number)
                        for d in self.get_vote_primary_departments()]
        votes = '"%s"' % '";"'.join(vote_numbers)
        cuts = [
            budget.get_financial_year_ref() + ':' + financial_year_start,
            budget.get_vote_number_ref() + ':' + votes
        ]
        if self.sphere.slug == 'provincial':
            cuts.append(budget.get_geo_ref() + ':"%s"' % self.name)
        drilldowns = [budget.get_function_ref()]
        result = budget.aggregate(cuts=cuts, drilldowns=drilldowns)
        functions = []
        for cell in result['cells']:
            functions.append({
                'name': cell[budget.get_function_ref()],
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

        ordering = ['vote_number', 'name']

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
        vocab_map = get_vocab_map()
        tags = [
            { 'vocabulary_id': vocab_map['spheres'],
              'name': self.government.sphere.slug },
            { 'vocabulary_id': vocab_map['financial_years'],
              'name': self.get_financial_year().slug },
        ]
        if self.government.sphere.slug == 'provincial':
            tags.append({
                'vocabulary_id': vocab_map['provinces'],
                'name': self.government.name,
            })
        dataset_fields = {
            'title': package_title(self),
            'name': package_id(self),
            'extras': [
                {'key': 'department_name', 'value': self.name},
                {'key': 'Department Name', 'value': self.name},
                {'key': 'department_name_slug', 'value': self.slug},
                {'key': 'Vote Number', 'value': self.vote_number},
                {'key': 'vote_number', 'value': self.vote_number},
                {'key': 'geographic_region_slug', 'value': self.government.slug},
                {'key': 'organisational_unit', 'value': 'department'},
            ],
            'owner_org': 'national-treasury',
            'license_id': 'other-pd',
            'tags': tags,
        }
        ckan.action.package_create(**dataset_fields)

    def upload_resource(self, local_path, overwrite=False):
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
            'package_id': dataset['id'],
            'name': resource_name(self),
            'upload': open(local_path, 'rb')
        }

        if resource and not overwrite:
            logger.info("Not overwriting existing resource %s to package %s",
                        local_path, dataset['id'])
            return

        if resource:
            logger.info("Re-uploading resource %s to package %s", local_path, dataset['id'])
            resource_fields['id'] = resource['id']
            result = ckan.action.resource_patch(**resource_fields)
        else:
            logger.info("Uploading resource %s to package %s", local_path, dataset['id'])
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
                    dataset = Dataset.from_package(package)
                    datasets[package['name']] = dataset
        return datasets.values()

    def get_programme_budgets(self):
        """
        get the budget totals for all the department programmes
        """
        if self._programme_budgets is not None:
            return self._programme_budgets
        budget = EstimatesOfExpenditure(
            financial_year_slug=self.get_financial_year().slug,
            sphere_slug=self.government.sphere.slug,
        )
        financial_year_start = self.get_financial_year().get_starting_year()
        cuts = [
            budget.get_financial_year_ref() + ':' + financial_year_start,
            budget.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(budget.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            budget.get_programme_number_ref(),
            budget.get_programme_name_ref(),
        ]
        result = budget.aggregate(cuts=cuts, drilldowns=drilldowns)
        programmes = []
        for cell in result['cells']:
            programmes.append({
                'name': cell[budget.get_programme_name_ref()],
                'total_budget': cell['value.sum']
            })
        self._programme_budgets = programmes
        return self._programme_budgets

    def get_expenditure_over_time(self):
        base_year = get_base_year()
        financial_year_start = self.get_financial_year().get_starting_year()
        financial_year_start_int = int(financial_year_start)
        financial_year_starts = [str(y) for y in xrange(financial_year_start_int-4, financial_year_start_int+3)]
        expenditure = {
            'base_financial_year': FinancialYear.slug_from_year_start(str(base_year)),
            'nominal': [],
            'real': [],
        }

        budget = EstimatesOfExpenditure(
            financial_year_slug=self.get_financial_year().slug,
            sphere_slug=self.government.sphere.slug,
        )
        cuts = [
            budget.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(budget.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            budget.get_financial_year_ref(),
            budget.get_phase_ref(),
        ]
        result = budget.aggregate(cuts=cuts, drilldowns=drilldowns)
        if result['cells']:
            cpi = get_cpi()
            for idx, financial_year_start in enumerate(financial_year_starts):
                phase = TRENDS_AND_ESTIMATES_PHASES[idx]
                cell = [
                    c for c in result['cells']
                    if c[budget.get_financial_year_ref()] == int(financial_year_start)
                    and c[budget.get_phase_ref()] == phase
                ][0]
                nominal = cell['value.sum']
                expenditure['nominal'].append({
                    'financial_year': FinancialYear.slug_from_year_start(financial_year_start),
                    'amount': nominal,
                    'phase': phase,
                })
                expenditure['real'].append({
                    'financial_year': FinancialYear.slug_from_year_start(financial_year_start),
                    'amount': int((Decimal(nominal)/cpi[financial_year_start]['index']) * 100),
                    'phase': phase,
                })

            return expenditure
        else:
            logger.warning("Missing expenditure data for %r budget year %s",
                           cuts, self.get_financial_year().slug)
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
        self.last_updated_date = kwargs['last_updated_date']
        self.license = kwargs['license']
        self.name = kwargs['name']
        self.resources = kwargs['resources']
        self.slug = kwargs['slug']
        self.intro = kwargs['intro']
        self.methodology = kwargs['methodology']
        self.organization_slug = kwargs['organization_slug']
        self.category = kwargs['category']

    @classmethod
    def from_package(cls, package):
        resources = []
        for resource in package['resources']:
            resources.append({
                'name': resource['name'],
                'description': resource['description'],
                'format': resource['format'],
                'url': resource['url'],
            })
        assert(len(package['categories']) < 2)
        return cls(
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
            category=package['categories'] and package['categories'][0]
        )

    @classmethod
    def fetch(cls, dataset_slug):
        logger.info("package_show id=%s", dataset_slug)
        package = ckan.action.package_show(id=dataset_slug)
        return cls.from_package(package)

    def get_url_path(self):
        if self.organization_slug == 'national-treasury' and self.category:
            category_slug = django_slugify(self.category)
            return "/datasets/%s/%s" % (category_slug, self.slug)
        elif self.organization_slug != 'national-treasury':
            return "/datasets/contributed-data/%s" % self.slug
        else:
            raise Exception("Not contributed and no category")

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

    @staticmethod
    def get_contributed_datasets():
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
            yield Dataset.from_package(package)


class Category():
    def __init__(self, **kwargs):
        self.slug = kwargs['slug']
        self.name = kwargs['name']

    @classmethod
    def get_by_slug(cls, category_slug):
        for tag in ckan.action.vocabulary_show(id='categories')['tags']:
            if django_slugify(tag['name']) == category_slug:
                return cls(slug=category_slug, name=tag['name'])
        raise Exception("Category %s not found" % category_slug)

    def get_datasets(self):
        query = {
            'q': '',
            'fq': 'vocab_categories:"%s"' % self.name,
            'rows': 1000,
        }
        response = ckan.action.package_search(**query)
        if response['count'] > 1000:
            raise Exception("Time to add paging")
        logger.info(
            "query %s\nto ckan returned %d results",
            pformat(query),
            len(response['results'])
        )
        for package in response['results']:
            yield Dataset.from_package(package)



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
    financial_year = department.get_financial_year().slug
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
    financial_year = department.get_financial_year().slug
    sphere = department.government.sphere
    geo_region = department.government.name
    if sphere.slug == 'provincial':
        return "%s Department: %s %s" % (geo_region, department.name, financial_year)
    elif sphere.slug == 'national':
        return "National Department: %s %s" % (department.name, financial_year)
    else:
        raise Exception('unknown sphere %r' % sphere)


def resource_name(department):
    return "Vote %d - %s" % (department.vote_number, department.name)


def get_base_year():
    cpi_year_slug = max(CPI_RESOURCE_IDS.keys())
    return int(cpi_year_slug[:4])-1


def get_cpi():
    cpi_year_slug = max(CPI_RESOURCE_IDS.keys())
    base_year = get_base_year()

    sql = '''
    SELECT "Year", "CPI" FROM "{}"
    ORDER BY "Year"
    '''.format(CPI_RESOURCE_IDS[cpi_year_slug])
    params = {
        'sql': sql
    }
    result = requests.get(CKAN_DATASTORE_URL, params=params)
    result.raise_for_status()
    cpi = result.json()['result']['records']
    base_year_index = None
    for idx, cell in enumerate(cpi):
        financial_year_start = cell['Year'][:4]
        cell['financial_year_start'] = financial_year_start
        if financial_year_start == str(base_year):
            base_year_index = idx
            cell['index'] = 100
    for idx in range(base_year_index-1, -1, -1):
        cpi[idx]['index'] = cpi[idx+1]['index'] / (1 + Decimal(cpi[idx+1]['CPI']))
    for idx in xrange(base_year_index+1, len(cpi)):
        cpi[idx]['index'] = cpi[idx-1]['index'] * (1 + Decimal(cpi[idx]['CPI']))
    cpi_dict = {}
    for cell in cpi:
        cpi_dict[cell['financial_year_start']] = cell
    return cpi_dict


def get_vocab_map():
    vocab_map = {}
    for vocab in ckan.action.vocabulary_list():
        vocab_map[vocab['name']] = vocab['id']
    return vocab_map
