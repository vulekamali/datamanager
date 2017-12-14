from django.conf import settings
from django.db import models
from django.utils.text import slugify
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

    @staticmethod
    def get_all():
        query = {
            'q': '',
            'facet.field': '["vocab_financial_years"]',
            'rows': 0,
        }
        response = ckan.action.package_search(**query)
        years_facet = response['search_facets']['vocab_financial_years']['items']
        years_facet.sort(key=lambda f: f['name'])
        for year in years_facet:
            year_obj, created = FinancialYear.objects.get_or_create(slug=year['name'])
            obj, created = Sphere.objects.get_or_create(
                financial_year=year_obj,
                name='National',
                slug='national'
            )
            obj, created = Sphere.objects.get_or_create(
                financial_year=year_obj,
                name='Provincial',
                slug='provincial'
            )
            yield year_obj

    def get_sphere(self, name):
        return getattr(self, name)

    def get_closest_match(self, department):
        sphere = getattr(self, department.government.sphere.name)
        government = sphere.get_government_by_slug(department.government.slug)
        department = government.get_department_by_slug(department.slug)
        if not department:
            return government, False
        return department, True


class Sphere(models.Model):
    organisational_unit = 'sphere'
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name="spheres")

    class Meta:
        unique_together = (
            ('financial_year', 'slug'),
            ('financial_year', 'name'),
        )

    @property
    def governments(self):
        if self._governments is None:
            self._fetch_governments()
        return self._governments

    def _fetch_governments(self):
        if self.name == 'national':
            self._governments = [Government('South Africa', self)]
        else:
            self._governments = []
            response = ckan.action.package_search(**{
                'q': '',
                'fq': 'vocab_financial_years:"%s"' % self.financial_year.slug,
                'facet.field': '["vocab_provinces"]',
                'rows': 0,
            })
            province_facet = response['search_facets']['vocab_provinces']['items']
            for province in province_facet:
                self._governments.append(Government(province['name'], self))

    def get_url_path(self):
        return "%s/%s" % (self.financial_year.get_url_path(), self.name)

    def get_government_by_slug(self, slug):
        return [g for g in self.governments if g.slug == slug][0]


class Government(models.Model):
    organisational_unit = 'government'
    sphere = models.ForeignKey(Sphere, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)

    def get_url_path(self):
        if self.sphere.name == 'national':
            return self.sphere.get_url_path()
        else:
            return "%s/%s" % (self.sphere.get_url_path(), self.slug)

    def get_department_by_slug(self, slug):
        departments = [d for d in self.departments if d.slug == slug]
        if len(departments) == 0:
            return None
        elif len(departments) == 1:
            return departments[0]
        else:
            raise Exception("More matching slugs than expected")

    @property
    def departments(self):
        if self._departments is None:
            self._fetch_departments()
        return self._departments

    def _fetch_departments(self):
        self._departments = []

        response = ckan.action.package_search(**{
            'q': '',
            'fq': ('vocab_financial_years:"%s"'
                   '+vocab_spheres:"%s"'
                   '+extras_geographic_region_slug:"%s"') % (
                       self.sphere.financial_year.slug,
                       self.sphere.name,
                       self.slug
                   ),
            'rows': 1000,
        })

        for package in response['results']:
            department_name = extras_get(package['extras'], 'department_name')
            vote_number = extras_get(package['extras'], 'vote_number')
            department = Department(self, department_name, int(vote_number), package['name'])
            self._departments.append(department)


class Department(models.Model):
    organisational_unit = 'department'
    government = models.ForeignKey(Government, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    vote_number = models.IntegerField(unique=True)
    intro = models.TextField()

    def get_url_path(self):
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)

    @property
    def narratives(self):
        if self._narratives is None:
            self._fetch_resources()
        return self._narratives

    @property
    def resources(self):
        if self._resources is None:
            self._fetch_resources()
        return self._resources

    def _fetch_resources(self):
        self._narratives = []
        self._resources = {}

        package = ckan.action.package_show(id=self._ckan_package_name)

        for resource in package['resources']:
            if re.match('^(ENE|EPRE) Section', resource['name']):
                name = re.sub('^(ENE|EPRE) Section - ', '', resource['name'])
                name_slug = slugify(name)
                logger.info("Downloading %s" % resource['url'])
                r = requests.get(resource['url'])
                r.raise_for_status()
                r.encoding = 'utf-8'
                content = r.text
                self._narratives.append({
                    'name': name,
                    'content': content,
                }),
            if resource['name'].startswith('Vote'):
                if self.government.sphere.name == 'provincial':
                    doc_short = "EPRE"
                    doc_long = "Estimates of Provincial Revenue and Expenditure"
                elif self.government.sphere.name == 'national':
                    doc_short = "ENE"
                    doc_long = "Estimates of National Expenditure"
                else:
                    raise Exception("unexpected sphere")
                name = "%s for %s" % (doc_short, resource['name'])
                description = ("The %s (%s) sets out the detailed spending "
                               "plans of each government department for the "
                               "coming year.") % (doc_long, doc_short)
                if name not in self._resources:
                    self._resources[name] = {
                        'description': description,
                        'formats': [],
                    }
                self._resources[name]['formats'].append({
                    'url': resource['url'],
                    'format': resource['format'],
                })


def extras_get(extras, key):
    return [e['value'] for e in extras if e['key'] == key][0]
