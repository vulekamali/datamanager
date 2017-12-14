from django.conf import settings
from django.db import models
import logging

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

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Sphere(models.Model):
    organisational_unit = 'sphere'
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)
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
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)

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
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)
    vote_number = models.IntegerField()
    intro = models.TextField()

    class Meta:
        unique_together = (
            ('government', 'slug'),
            ('government', 'name'),
            ('government', 'vote_number'),
        )

    def get_url_path(self):
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)

    def get_resources(self):
        resources = {}

        query = {
            'q': '',
            'fq': ('vocab_financial_years:"%s"'
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

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.get_url_path())


class Programme(models.Model):
    organisational_unit = 'programme'
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programmes")
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)
