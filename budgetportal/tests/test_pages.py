from budgetportal.models import FinancialYear, Sphere, Government, Department
from django.conf import settings
from django.test import TestCase, Client
from mock import patch, Mock

# Hacky make sure we don't call out to openspending.
import requests

requests.get = Mock
requests.Session = Mock


class BasicPagesTestCase(TestCase):
    fixtures = ["video-language", "faq"]

    def setUp(self):
        FinancialYear.objects.create(slug="2015-16", published=True)
        FinancialYear.objects.create(slug="2016-17", published=True)
        FinancialYear.objects.create(slug="2017-18", published=True)
        FinancialYear.objects.create(slug="2018-19", published=True)
        FinancialYear.objects.create(slug="2019-20", published=True)
        for year in FinancialYear.objects.all():
            # spheres
            national = Sphere.objects.create(financial_year=year, name="National")
            Sphere.objects.create(financial_year=year, name="Provincial")

            # governments
            south_africa = Government.objects.create(
                sphere=national, name="South Africa"
            )

            # departments
            Department.objects.create(
                government=south_africa, name="The Presidency", vote_number=1, intro=""
            )
        ckan_patch = patch("budgetportal.models.ckan")
        CKANMockClass = ckan_patch.start()
        CKANMockClass.action.package_search.return_value = {"results": []}
        self.addCleanup(ckan_patch.stop)

        ckan_patch = patch("budgetportal.datasets.ckan")
        CKANMockClass = ckan_patch.start()
        CKANMockClass.action.package_search.return_value = {"results": []}
        # self.addCleanup(ckan_patch.stop)

        CKANMockClass.action.group_show.return_value = {
            "name": "test",
            "description": "basic-test-description",
            "title": "test-slug",
        }
        # self.addCleanup(ckan_patch.stop)

        CKANMockClass.action.package_show.return_value = {
            "state": "",
            "resources": [],
            "groups": [
                {
                    "name": "test-slug",
                    "description": "basic-test-description",
                    "title": "test-slug",
                }
            ],
            "name": "test-2018-19",
            "title": "Test 2018/19",
            "id": "9c7af295",
            "metadata_created": "2018-11-30T05:06:49.588395",
            "metadata_modified": "2018-12-03T10:07:22.333285",
            "author": "Vulekamali ",
            "author_email": "",
            "license_title": "Creative Commons Attribution Share-Alike",
            "license_url": "http://www.opendefinition.org/licenses/cc-by-sa",
            "organization": {"name": "basic-organization-slug"},
        }
        self.addCleanup(ckan_patch.stop)

        dataset_patch = patch(
            "budgetportal.datasets.Dataset.get_latest_cpi_resource",
            return_value=("2018-19", "5b315ff0-55e9-4ba8-b88c-2d70093bfe9d"),
        )
        dataset_patch.start()
        self.addCleanup(dataset_patch.stop)

    def test_overview_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get("/")

        self.assertContains(response, '<a class="NavBar-link is-active" href="/">')
        self.assertContains(response, "About Vulekamali")
        self.assertContains(
            response,
            "Vulekamali is a project by the South African National Treasury and Imali Yethu",
        )

    def test_departments_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/2019-20/departments")

        self.assertContains(response, "Department Budgets for 2019-20 - vulekamali")

    def test_department_detail_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/2019-20/national/departments/the-presidency")

        self.assertContains(
            response, "The Presidency budget data for the 2019-20 financial year"
        )

    def test_department_preview_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/2019-20/previews/national/south-africa/social-development")

        self.assertContains(response, '<div data-webapp="preview-pages"></div>')
        self.assertContains(
            response,
            '=https://vulekamali.gov.za/2019-20/previews/national/south-africa/social-development">',
        )

    def test_about_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/about")

        self.assertContains(
            response, "Learn more about the new Online Budget Data Portal"
        )

    def test_events_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/events")

        self.assertContains(response, "Join us at a Vulekamali event in your area")

    def test_videos_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/videos")

        self.assertContains(
            response, "Learn more about the new Online Budget Data Portal"
        )

    def test_terms_and_conditions_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/terms-and-conditions")

        self.assertContains(response, "Users are encouraged to utilise this data")

    def test_resources_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/resources")
        content = response.content
        self.assertContains(response, "The Budget Process and Public Participation")

    def test_glossary_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/glossary")

        self.assertContains(response, "<title>Glossary - vulekamali</title>")

    def test_faq_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/faq")

        self.assertContains(response, "Frequently Asked Questions (FAQ)")
        self.assertContains(response, "When is the budget data updated?")
        self.assertContains(
            response,
            "A new budget is produced by government and added to the portal every financial year",
        )

    def test_guides_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/guides")

        self.assertContains(response, "Dataset Guides")
        self.assertContains(response, "Estimates of National Expenditure (ENE)")
        self.assertContains(response, "Performance and Expenditure Reviews (PER)")

    def test_guide_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/guides/estimates-of-national-expenditure")

        self.assertContains(
            response,
            "The Estimates of National Expenditure (ENE) publications describe in detail",
        )

    def test_dataset_category_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/datasets")

        self.assertContains(response, "Data and Analysis")

    def test_dataset_category_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/datasets/test-slug")

        self.assertContains(response, "<title>test-slug - vulekamali</title>")
        self.assertContains(response, "basic-test-description")
        self.assertContains(response, "Learn more about test-slug")

    def test_search_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get(
            "/2019-20/search-result/?search_type=full-search&search_string=a&search=a"
        )

        self.assertContains(response, "<title>Search Results - vulekamali</title>")
        self.assertContains(
            response,
            '<div data-component="SearchResult" data-year="2019-20" data-root></div>',
        )

    def test_focus_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/2019-20/focus/social-development")

        self.assertContains(response, '<div data-webapp="focus-areas-preview"></div>')

    def test_dataset_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/datasets/test-slug/test-2018-19")

        self.assertContains(response, "<title>Test 2018/19 - vulekamali</title>")
        self.assertContains(response, '<a href="/datasets/test-slug">test-slug</a>')
        self.assertContains(response, "Test 2018/19")

    def test_infrastructure_projects_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/infrastructure-projects")

        self.assertContains(
            response,
            '<div data-webapp="infrastructure-pages" class="infrastructure-projects"></div>',
        )
