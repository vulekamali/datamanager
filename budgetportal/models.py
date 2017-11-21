from django.utils.text import slugify
import requests
from requests.adapters import HTTPAdapter


class Government():
    organisational_unit = 'government'

    def __init__(self, name, sphere):
        self.name = name
        self.slug = slugify(self.name)
        self.sphere = sphere
        self.departments = []

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


class Department():
    organisational_unit = 'department'

    def __init__(self, government, name, vote_number, narrative):
        self.government = government
        self.name = name
        self.slug = slugify(self.name)
        self.vote_number = vote_number
        self.narrative = narrative

    def get(financial_year, sphere, geographic_region_slug, department_name_slug):
        fq = ('vocab_financial_years:%s'
              ' +vocab_spheres:%s'
              ' +extras_geographic_region_slug:%s'
              ' +extras_department_name_slug:%s') % (
                  financial_year,
                  sphere,
                  geographic_region_slug,
                  department_name_slug,
              )
        response = ckan.action.package_search(fq=fq)
        if response['count'] == 1:
            return Department(government, name, vote_number, narrative)
        else:
            return None

    @classmethod
    def from_ckan_package(cls, government, package):
        narrative = {}
        for resource in package['resources']:
            if resource['name'].startswith('ENE Section - '):
                name = resource['name'].replace('ENE Section - ', '')
                name_slug = slugify(name)
                print "Downloading %s" % resource['url']
                r = requests.get(resource['url'])
                r.raise_for_status()
                r.encoding = 'utf-8'
                content = r.text
                narrative[name_slug] = {
                    'name': name,
                    'content': content,
                }
        return cls(
            government,
            extras_get(package['extras'], 'Department Name'),
            int(extras_get(package['extras'], 'Vote Number')),
            narrative,
        )

    def get_url_path(self):
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)


class Sphere():
    organisational_unit = 'sphere'

    def __init__(self, financial_year, name):
        self.financial_year = financial_year
        self.name = name
        self.governments = {}

    def get_url_path(self):
        return "%s/%s" % (self.financial_year.get_url_path(), self.name)

    def get_government_by_slug(self, slug):
        return [g for g in self.governments.values() if g.slug == slug][0]


class FinancialYear():
    organisational_unit = 'financial_year'

    def __init__(self, id):
        self.id = id
        self.national = Sphere(self, 'national')
        self.provincial = Sphere(self, 'provincial')

    def get_url_path(self):
        return "/%s" % self.id

    def get_closest_match(self, department):
        sphere = getattr(self, department.government.sphere.name)
        government = sphere.get_government_by_slug(department.government.slug)
        department = government.get_department_by_slug(department.slug)
        if not department:
            return government, False
        return department, True

    def get_sphere(self, name):
        return getattr(self, name)


def extras_get(extras, key):
    return [e['value'] for e in extras if e['key'] == key][0]
