from django.utils.text import slugify
from django.conf import settings

ckan = settings.CKAN


class Department():
    organisational_unit = 'department'

    def __init__(self, government, name, vote_number):
        self.government = government
        self.name = name
        self.slug = slugify(self.name)
        self.vote_number = vote_number

    def get_url_path(self):
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)


class Government():
    organisational_unit = 'government'

    def __init__(self, name, sphere):
        self.name = name
        self.slug = slugify(self.name)
        self.sphere = sphere
        self._departments = None

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
                       self.sphere.financial_year.id,
                       self.sphere.name,
                       self.slug
                   ),
            'rows': 1000,
        })

        for package in response['results']:
            department_name = extras_get(package['extras'], 'department_name')
            vote_number = extras_get(package['extras'], 'vote_number')
            self._departments.append(Department(self, department_name, int(vote_number)))


class Sphere():
    organisational_unit = 'sphere'

    def __init__(self, financial_year, name):
        self.financial_year = financial_year
        self.name = name
        self._governments = None

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
                'fq': 'vocab_financial_years:"%s"' % self.financial_year.id,
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


class FinancialYear():
    organisational_unit = 'financial_year'

    class Meta:
        managed = False

    def __init__(self, id):
        self.id = id
        self.national = Sphere(self, 'national')
        self.provincial = Sphere(self, 'provincial')

    def get_url_path(self):
        return "/%s" % self.id

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
            yield FinancialYear(year['name'])

    def get_sphere(self, name):
        return getattr(self, name)

    def get_closest_match(self, department):
        sphere = getattr(self, department.government.sphere.name)
        government = sphere.get_government_by_slug(department.government.slug)
        department = government.get_department_by_slug(department.slug)
        if not department:
            return government, False
        return department, True


def extras_get(extras, key):
    return [e['value'] for e in extras if e['key'] == key][0]
