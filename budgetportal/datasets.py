
from budgetportal.openspending import (
    EstimatesOfExpenditure,
    AdjustedEstimatesOfExpenditure,
    ExpenditureTimeSeries
)
from tempfile import mkdtemp
import os
import shutil
import urlparse
import logging
from django.conf import settings
from pprint import pformat
from ckanapi import NotFound
import urllib


logger = logging.getLogger(__name__)
ckan = settings.CKAN


class Dataset():
    """
    Represents a CKAN dataset (AKA package)
    """

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
                'id': resource['id'],

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
            if not name and (resource['format'] == format):
                return resource

    def create_resource(self, name, format, url):
        try:
            # urlopen doesn't encode spaces for you
            # https://bugs.python.org/issue13359
            if ' ' in url:
                url = url.replace(' ', '%20')
            logger.info("Downloading %s to upload to package %s",
                        url, self.slug)
            tempdir = mkdtemp(prefix="budgetportal")
            basename = urllib.unquote(
                os.path.basename(urlparse.urlparse(url).path))
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
            logger.info("Upload result: resource '%s' to package %s %r",
                        name, self.slug, result)
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
        try:
            api_resource = filter(
                lambda r: r['format'].lower() == 'openspending api',
                self.resources
            )[0]
        except IndexError:
            return None
        api_class_mapping = {
            'estimates-of-national-expenditure': EstimatesOfExpenditure,
            'estimates-of-provincial-expenditure': EstimatesOfExpenditure,
            'adjusted-estimates-of-national-expenditure': AdjustedEstimatesOfExpenditure,
            'adjusted-estimates-of-provincial-expenditure': AdjustedEstimatesOfExpenditure,
            'budgeted-and-actual-national-expenditure': ExpenditureTimeSeries,
            'budgeted-and-actual-provincial-expenditure': ExpenditureTimeSeries,
            'consolidated-expenditure-budget': ExpenditureTimeSeries,
        }
        api_class = api_class_mapping[self.category.slug]
        self._openspending_api = api_class(api_resource['url'])
        return self._openspending_api


    @staticmethod
    def get_latest_cpi_resource():
        """
        Find the latest CPI dataset that was uploaded and return its financial
        year and the id of its CSV resource.

        :returns: latest financial year, resource id
        """
        # Get all the datasets in CPI data group /group/cpi-inflation
        query = {
            'q': '',
            'fq': ''.join([
                '+organization:"national-treasury"',
                '+groups:"cpi-inflation"',
            ]),
            'rows': 1000,
        }
        response = ckan.action.package_search(**query)
        assert response['results']

        results = response['results']

        def get_financial_year_and_resources(dataset):
            assert 'financial_year' in dataset and len(dataset['financial_year']) == 1

            return {
                'financial_year': dataset['financial_year'][0],
                'resources': dataset['resources'],
            }

        # Get the dataset with the latest financial_year
        latest_dataset = max(map(get_financial_year_and_resources, results),
            key=lambda x: x['financial_year'])

        # Get the only resource with the CSV format
        resources = filter(lambda x: x.get('format', None) == 'CSV',
            latest_dataset['resources'])

        assert len(resources) == 1 and 'id' in resources[0]

        return latest_dataset['financial_year'], resources[0]['id']


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


class PackageDeletedException(Exception):
    pass


class PackageWithoutGroupException(Exception):
    pass


def package_is_contributed(package):
    return len(package['groups']) == 0 \
        and package['organization']['name'] != 'national-treasury'


def none_if_empty_or_missing(dict, key):
    if dict.get(key, None):
        return dict.get(key)
    else:
        return None


def get_expenditure_time_series_dataset(sphere_slug):
    query = {
        'q': '',
        'fq': ''.join([
            '+organization:"national-treasury"',
            '+groups:"budgeted-and-actual-%s-expenditure"' % sphere_slug,
        ]),
        'rows': 1000,
    }
    response = ckan.action.package_search(**query)
    if response['results']:
        package = response['results'][0]
        return Dataset.from_package(package)
    else:
        return None


def get_consolidated_expenditure_budget_dataset():
    query = {
        'q': '',
        'fq': ''.join([
            '+organization:"national-treasury"',
            '+groups:"consolidated-expenditure-budget"',
        ]),
        'rows': 1000,
    }
    response = ckan.action.package_search(**query)
    if response['results']:
        package = response['results'][0]
        return Dataset.from_package(package)
    else:
        return None
