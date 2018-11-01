from autoslug import AutoSlugField
from budgetportal.openspending import EstimatesOfExpenditure
from ckanapi import NotFound
from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import models
from django.utils.text import slugify as django_slugify
from itertools import groupby
from partial_index import PartialIndex
from pprint import pformat
from tempfile import mkdtemp
import logging
import os
import re
import requests
import shutil
import urllib
import urlparse

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
        ordering = ['-financial_year__slug', 'name']

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
        budget = self.get_estimates_of_expenditure_dataset().get_openspending_api()
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
    name = models.CharField(max_length=200, help_text="The department name must precisely match the text used in the Appropriation Bill. All datasets must be normalised to match this name. Beware that changing this name might cause a mismatch with already-published datasets which might need to be update to match this.")
    slug = AutoSlugField(populate_from='name', max_length=200, always_update=True, editable=True)
    vote_number = models.IntegerField()
    is_vote_primary = models.BooleanField(default=True)
    intro = models.TextField()
    _programme_budgets = None
    _econ_by_programme_budgets = None
    _prog_by_econ_budgets = None
    _estimates_of_econ_classes_expenditure_dataset = None
    _estimates_of_subprogramme_expenditure_dataset = None

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        if self.pk:
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

    def create_dataset(self, name, title, group_name):
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
            'title': title,
            'name': name,
            'groups': [{'name': group_name}],
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
        logger.info("Creating package with %r", dataset_fields)
        return Dataset.from_package(ckan.action.package_create(**dataset_fields))

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

    def get_dataset(self, group_name, name=None):
        """
        Get a dataset correctly annotated to match this department.
        If name isn't provided, still assume there's just one dataset
        in the specified group categorised to match this department.
        """
        query = {
            'q': '',
            'fq': ('+organization:"national-treasury"'
                   '+vocab_financial_years:"%s"'
                   '+vocab_spheres:"%s"'
                   '+extras_s_geographic_region_slug:"%s"'
                   '+extras_s_department_name_slug:"%s"'
                   '+groups:"%s"') % (
                       self.government.sphere.financial_year.slug,
                       self.government.sphere.slug,
                       self.government.slug,
                       self.get_primary_department().slug,
                       group_name,
                   ),
            'rows': 1,
        }
        if name:
            query['fq'] += '+name:"%s"' % name
        response = ckan.action.package_search(**query)
        logger.info(
            "query %s\nreturned %d results",
            pformat(query),
            len(response['results'])
        )
        if response['results']:
            assert(len(response['results']) == 1)
            return Dataset.from_package(response['results'][0])

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
        fq_group = '+(*:* NOT groups:["" TO *])'
        fq_year = self._get_financial_year_query()
        fq_sphere = '+vocab_spheres:"%s"' % self.government.sphere.slug
        fq_government = self._get_government_query()
        fq_functions = self._get_functions_query()
        fq_no_functions = none_selected_query('vocab_functions')
        queries = [
            (fq_org, fq_group, fq_year, fq_sphere, fq_government, fq_functions),
            (fq_org, fq_group, fq_sphere, fq_government, fq_functions),
            (fq_org, fq_group, fq_year, fq_sphere, fq_functions),
            (fq_org, fq_group, fq_sphere, fq_functions),
            (fq_org, fq_group, fq_functions),
            (fq_org, fq_group, fq_no_functions),
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

    def get_estimates_of_econ_classes_expenditure_dataset(self):
        if self._estimates_of_econ_classes_expenditure_dataset is not None:
            return self._estimates_of_econ_classes_expenditure_dataset
        query = {
            'q': '',
            'fq': ''.join([
                '+organization:"national-treasury"',
                '+groups:"estimates-of-%s-expenditure"' % self.government.sphere.slug,
                '+vocab_financial_years:"%s"' % self.get_financial_year().slug,
                '+vocab_dimensions:"Economic classification 1"',
                '+vocab_dimensions:"Economic classification 2"',
            ]),
            'rows': 1000,
        }
        response = ckan.action.package_search(**query)
        if response['results']:
            package = response['results'][0]
            self._estimates_of_econ_classes_expenditure_dataset = Dataset.from_package(package)
            return self._estimates_of_econ_classes_expenditure_dataset
        else:
            return None

    def get_estimates_of_subprogramme_expenditure_dataset(self):
        if self._estimates_of_subprogramme_expenditure_dataset is not None:
            return self._estimates_of_econ_classes_expenditure_dataset
        query = {
            'q': '',
            'fq': ''.join([
                '+organization:"national-treasury"',
                '+groups:"estimates-of-%s-expenditure"' % self.government.sphere.slug,
                '+vocab_financial_years:"%s"' % self.get_financial_year().slug,
                '+vocab_dimensions:"Sub-programme"',
            ]),
            'rows': 1000,
        }
        response = ckan.action.package_search(**query)
        if response['results']:
            package = response['results'][0]
            self._estimates_of_subprogramme_expenditure_dataset = Dataset.from_package(package)
            return self._estimates_of_subprogramme_expenditure_dataset
        else:
            return None

    def get_programme_budgets(self):
        """
        get the budget totals for all the department programmes
        """
        if self._programme_budgets is not None:
            return self._programme_budgets
        dataset = self.get_estimates_of_econ_classes_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        financial_year_start = self.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ':' + financial_year_start,
            openspending_api.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(openspending_api.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            openspending_api.get_programme_number_ref(),
            openspending_api.get_programme_name_ref(),
        ]
        result = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        programmes = []
        for cell in result['cells']:
            programmes.append({
                'name': cell[openspending_api.get_programme_name_ref()],
                'total_budget': cell['value.sum']
            })
        self._programme_budgets = {
            'programme_budgets': programmes,
            'dataset_detail_page': dataset.get_url_path(),
        }
        return self._programme_budgets

    def get_econ_by_programme_budgets(self):
        """
        get the econ class 2 budget totals for all the department programmes
        """
        if self._econ_by_programme_budgets is not None:
            return self._econ_by_programme_budgets
        dataset = self.get_estimates_of_econ_classes_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        financial_year_start = self.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ':' + financial_year_start,
            openspending_api.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(openspending_api.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            openspending_api.get_programme_number_ref(),
            openspending_api.get_programme_name_ref(),
            openspending_api.get_econ_class_1_ref(),
            openspending_api.get_econ_class_2_ref(),
        ]
        result = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        prog_func = lambda cell: cell[openspending_api.get_programme_name_ref()]
        econ1_func = lambda cell: cell[openspending_api.get_econ_class_1_ref()]
        total_budget_fun = lambda x: x['total_budget']
        programmes = []
        prog_sorted = sorted(result['cells'], key=prog_func)
        for programme_name, programme_group in groupby(prog_sorted, prog_func):
            econ_class_1s = []
            econ1_sorted = sorted(programme_group, key=econ1_func)
            for econ1_name, econ1_group in groupby(econ1_sorted, econ1_func):
                econ_class_2s = []
                for cell in econ1_group:
                    if cell['value.sum']:
                        ref = openspending_api.get_econ_class_2_ref()
                        econ_class_2s.append({
                            'type': 'economic_classification_2',
                            'name': cell[ref],
                            'total_budget': cell['value.sum'],
                        })
                if econ_class_2s:
                    econ_class_1s.append({
                        'type': 'economic_classification_1',
                        'name': econ1_name,
                        'items': sorted(econ_class_2s, key=total_budget_fun, reverse=True),
                    })
            if econ_class_1s:
                programmes.append({
                    'type': 'programme',
                    'name': programme_name,
                    'items': econ_class_1s,
                })

        self._econ_by_programme_budgets = {
            'programmes': programmes,
            'dataset_detail_page': dataset.get_url_path(),
        }
        return self._econ_by_programme_budgets

    def get_prog_by_econ_budgets(self):
        """
        get the programme budget totals for each economic classification at level 2
        """
        if self._prog_by_econ_budgets is not None:
            return self._prog_by_econ_budgets
        dataset = self.get_estimates_of_econ_classes_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        financial_year_start = self.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ':' + financial_year_start,
            openspending_api.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(openspending_api.get_geo_ref() + ':"%s"' % self.government.name)

        drilldowns = [
            openspending_api.get_programme_number_ref(),
            openspending_api.get_programme_name_ref(),
            openspending_api.get_econ_class_1_ref(),
            openspending_api.get_econ_class_2_ref(),
        ]
        result = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        econ1_2_func = lambda cell: " - ".join([
            cell[openspending_api.get_econ_class_1_ref()],
            cell[openspending_api.get_econ_class_2_ref()],
        ])
        prog_func = lambda cell: cell[openspending_api.get_programme_name_ref()]
        total_budget_fun = lambda x: x['total_budget']
        econ_classes = []
        econ_sorted = sorted(result['cells'], key=econ1_2_func)
        for econ_class_name, econ_class_group in groupby(econ_sorted, econ1_2_func):
            programmes = []
            for cell in econ_class_group:
                if cell['value.sum']:
                    programmes.append({
                        'type': 'programme',
                        'name': cell[openspending_api.get_programme_name_ref()],
                        'total_budget': cell['value.sum'],
                    })
            if programmes:
                econ_classes.append({
                    'type': 'economic_classification_1_and_2',
                    'name': econ_class_name,
                    'items': sorted(programmes, key=total_budget_fun, reverse=True),
                })
        self._prog_by_econ_budgets = {
            'econ_classes': econ_classes,
            'dataset_detail_page': dataset.get_url_path(),
            'department_data_csv': openspending_api.aggregate_url(cuts=cuts,
                                                                  drilldowns=openspending_api.get_all_drilldowns(),
                                                                  csv=True)
        }
        return self._prog_by_econ_budgets

    def get_subprog_budgets(self):
        """
        get the sub-programme budget totals for each programme
        """
        dataset = self.get_estimates_of_subprogramme_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        financial_year_start = self.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ':' + financial_year_start,
            openspending_api.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(openspending_api.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            openspending_api.get_programme_number_ref(),
            openspending_api.get_programme_name_ref(),
            openspending_api.get_subprogramme_name_ref(),
        ]
        result = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        prog_func = lambda cell: cell[openspending_api.get_programme_name_ref()]
        total_budget_fun = lambda x: x['total_budget']
        programmes = []
        programme_sorted = sorted(result['cells'], key=prog_func)
        for prog_name, prog_group in groupby(programme_sorted, prog_func):
            subprogrammes = []
            for cell in prog_group:
                if cell['value.sum']:
                    subprogrammes.append({
                        'type': 'subprogramme',
                        'name': cell[openspending_api.get_subprogramme_name_ref()],
                        'total_budget': cell['value.sum'],
                    })
            if subprogrammes:
                programmes.append({
                    'type': 'programme',
                    'name': prog_name,
                    'items': sorted(subprogrammes, key=total_budget_fun, reverse=True),
                })
        return {
            'programmes': programmes,
            'dataset_detail_page': dataset.get_url_path(),
        }

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

        dataset = self.get_estimates_of_econ_classes_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        cuts = [
            openspending_api.get_department_name_ref() + ':"' + self.name + '"',
        ]
        if self.government.sphere.slug == 'provincial':
            cuts.append(openspending_api.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            openspending_api.get_financial_year_ref(),
            openspending_api.get_phase_ref(),
        ]
        result = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        if result['cells']:
            cpi = get_cpi()
            for idx, financial_year_start in enumerate(financial_year_starts):
                phase = TRENDS_AND_ESTIMATES_PHASES[idx]
                cell = [
                    c for c in result['cells']
                    if c[openspending_api.get_financial_year_ref()] == int(financial_year_start)
                    and c[openspending_api.get_phase_ref()] == phase
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

            return {
                'expenditure': expenditure,
                'dataset_detail_page': dataset.get_url_path(),
            }
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


class PackageDeletedException(Exception):
    pass

class PackageWithoutGroupException(Exception):
    pass

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
        self.intro_short = kwargs['intro_short']
        self.methodology = kwargs['methodology']
        self.key_points = kwargs['key_points']
        self.use_for = kwargs['use_for']
        self.usage = kwargs['usage']
        self.organization_slug = kwargs['organization_slug']
        self.category = kwargs['category']
        self._openspending_api = None
        self.package = kwargs['package']

    @classmethod
    def from_package(cls, package):
        if package['state'] == 'deleted':
            raise PackageDeletedException

        resources = []
        for resource in package['resources']:
            resources.append({
                'name': resource['name'],
                'description': resource['description'],
                'format': resource['format'],
                'url': resource['url'],
            })

        if package_is_contributed(package):
            category = Category.contributed()
        else:
            if not package['groups']:
                raise PackageWithoutGroupException
            category = Category.from_group(package['groups'][0])

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
            intro=none_if_empty_or_missing(package, 'notes'),
            intro_short=none_if_empty_or_missing(package, 'notes_short'),
            methodology=none_if_empty_or_missing(package, 'methodology'),
            key_points=none_if_empty_or_missing(package, 'key_points'),
            use_for=none_if_empty_or_missing(package, 'use_for'),
            usage=none_if_empty_or_missing(package, 'usage'),
            resources=resources,
            organization_slug=package['organization']['name'],
            category=category,
            package=package,
        )

    @classmethod
    def fetch(cls, dataset_slug):
        logger.info("package_show id=%s", dataset_slug)
        try:
            package = ckan.action.package_show(id=dataset_slug)
            return cls.from_package(package)
        except NotFound:
            logger.info("Package with name %s not found.", dataset_slug)
            return None

    def get_url_path(self):
        return "/datasets/%s/%s" % (self.category.slug, self.slug)

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

    def get_resource(self, format, name=None):
        """
        Returns the first matching resource, or None if none match.
        """
        for resource in self.resources:
            if (name
                and resource['name'] == name
                and resource['format'] == format):
                return resource
            # if name wasn't provided, just match first item with this format
            if (resource['format'] == format):
                return resource

    def create_resource(self, name, format, url):
        try:
            # urlopen doesn't encode spaces for you https://bugs.python.org/issue13359
            if ' ' in url:
                url = url.replace(' ', '%20')
            logger.info("Downloading %s to upload to package %s", url, self.slug)
            tempdir = mkdtemp(prefix="budgetportal")
            basename = urllib.unquote(os.path.basename(urlparse.urlparse(url).path))
            filename = os.path.join(tempdir, basename)
            logger.info("Downloading %s to %s", url, filename)
            urllib.urlretrieve(url, filename)[0]

            logger.info("Uploading file %s as resource '%s' to package %s",
                        filename, name, self.slug)
            resource_fields = {
                'package_id': self.slug,
                'name': name,
                'upload': open(filename, 'rb'),
                'format': format,
            }
            result = ckan.action.resource_create(**resource_fields)
            logger.info("Upload result: resource '%s' to package %s %r", name, self.slug, result)
            self.resources.append(result)
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            logger.info("Deleting temporary directory %s", tempdir)
            shutil.rmtree(tempdir)

    @staticmethod
    def get_contributed_datasets():
        query = {
            'q': '',
            'fq': '-organization:"national-treasury" AND (*:* NOT groups:["" TO *])',
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

    def get_openspending_api(self):
        if self._openspending_api is not None:
            return self._openspending_api
        api_resource = filter(
            lambda r: r['format'] == 'OpenSpending API',
            self.resources
        )[0]
        self._openspending_api = EstimatesOfExpenditure(api_resource['url'])
        return self._openspending_api



class Category():
    excluded_groups = {
        'budget-vote-documents',
        'adjusted-budget-vote-documents',
    }

    def __init__(self, **kwargs):
        self.slug = kwargs['slug']
        self.name = kwargs['name']
        self.description = kwargs['description']

    @classmethod
    def get_all(cls):
        categories = [cls.contributed()]
        for group in ckan.action.group_list(all_fields=True):
            if group['name'] not in cls.excluded_groups:
                categories.append(cls.from_group(group))
        return sorted(categories, key=lambda c: c.name)

    @classmethod
    def get_by_slug(cls, category_slug):
        if category_slug == 'contributed':
            return cls.contributed()
        else:
            try:
                group = ckan.action.group_show(id=category_slug)
                return cls.from_group(group)
            except NotFound:
                logger.info("Group with name %s not found.", category_slug)
                return None

    @classmethod
    def from_group(cls, group):
        return cls(
            slug=group['name'],
            description=group['description'],
            name=group['title'],
        )

    def get_datasets(self):
        datasets = []
        if self.slug == 'contributed':
            datasets = Dataset.get_contributed_datasets()
        else:
            packages = ckan.action.group_package_show(id=self.slug, limit=1000)
            if len(packages) == 1000:
                raise Exception("Too many packages to list like this")
            for package in packages:
                datasets.append(Dataset.from_package(package))
        return sorted(datasets, key=lambda d: d.name)

    def get_url_path(self):
        return "/datasets/%s" % self.slug

    @classmethod
    def contributed(cls):
        return cls(
            name='Contributed data and analysis',
            slug='contributed',
            description=("Data and analysis contributed by other organisations "
                         "on South African government budgets. ")
        )


# https://stackoverflow.com/questions/35633037/search-for-document-in-solr-where-a-multivalue-field-is-either-empty-or-has-a-sp
def none_selected_query(vocab_name):
    """Match items where none of the options in a custom vocab tag is selected"""
    return '+(*:* NOT %s:["" TO *])' % vocab_name


def extras_set(extras, key, value):
    for extra in extras:
        if extra['key'] == key:
            extra['value'] = value
            break


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


def package_is_contributed(package):
    return len(package['groups']) == 0 \
        and package['organization']['name'] != 'national-treasury'


def none_if_empty_or_missing(dict, key):
    if dict.get(key, None):
        return dict.get(key)
    else:
        return None
