from budgetportal.models import (
    CategoryGuide,
    Department,
    FinancialYear,
    Government,
    Notice,
    Sphere,
)
from django.test import Client, TestCase
from mock import MagicMock, patch


class BasicPagesTestCase(TestCase):
    fixtures = ["video-language", "faq", "homepage", "menu", "test-guides-pages"]

    def setUp(self):
        self.mock_openspending_api = MagicMock()
        self.mock_openspending_api.get_adjustment_kind_ref.return_value = (
            "adjustment_kind_ref"
        )
        self.mock_openspending_api.aggregate_url.return_value = "some-url"
        self.mock_openspending_api.get_function_ref.return_value = (
            "function_group.function_group"
        )
        self.mock_openspending_api.get_year_ref.return_value = (
            "function_group.function_group"
        )
        self.mock_openspending_api.get_financial_year_ref.return_value = (
            "financial_year.financial_year"
        )

        FinancialYear.objects.create(slug="2015-16", published=True)
        FinancialYear.objects.create(slug="2016-17", published=True)
        FinancialYear.objects.create(slug="2017-18", published=True)
        FinancialYear.objects.create(slug="2018-19", published=True)
        FinancialYear.objects.create(slug="2019-20", published=True)
        for year in FinancialYear.objects.all():
            # spheres
            national = Sphere.objects.create(financial_year=year, name="National")
            provincial = Sphere.objects.create(financial_year=year, name="Provincial")

            # governments
            south_africa = Government.objects.create(
                sphere=national, name="South Africa"
            )
            fake_cape = Government.objects.create(sphere=provincial, name="Fake Cape")

            # departments
            Department.objects.create(
                government=south_africa, name="The Presidency", vote_number=1, intro=""
            )
            Department.objects.create(
                government=fake_cape, name="Fake Health", vote_number=1, intro=""
            )
        models_ckan_patch = patch("budgetportal.models.government.ckan")
        ModelsCKANMockClass = models_ckan_patch.start()
        ModelsCKANMockClass.action.package_search.return_value = {"results": []}
        self.addCleanup(models_ckan_patch.stop)

        datasets_ckan_patch = patch("budgetportal.datasets.ckan")
        DatasetsCKANMockClass = datasets_ckan_patch.start()
        DatasetsCKANMockClass.action.package_search.return_value = {"results": []}
        DatasetsCKANMockClass.action.group_show.return_value = {
            "name": "test",
            "description": "basic-test-description",
            "title": "test-slug",
        }
        DatasetsCKANMockClass.action.package_show.return_value = {
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
        self.addCleanup(datasets_ckan_patch.stop)

        dataset_patch = patch(
            "budgetportal.datasets.Dataset.get_latest_cpi_resource",
            return_value=("2018-19", "5b315ff0-55e9-4ba8-b88c-2d70093bfe9d"),
        )
        dataset_patch.start()
        self.addCleanup(dataset_patch.stop)

    def test_homepage(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get("/")

        self.assertContains(response, 'class="NavBar-link is-active')
        self.assertContains(response, "About Vulekamali")
        self.assertContains(
            response,
            "Vulekamali is a project by the South African National Treasury and Imali Yethu",
        )
        self.assertNotContains(response, "Important notice")

    def test_homepage_with_notice(self):
        """Test that it exists and that the correct years are linked"""
        Notice.objects.create(description="test", content="Important notice")
        c = Client()
        response = c.get("/")

        self.assertContains(response, 'class="NavBar-link is-active')
        self.assertContains(response, "About Vulekamali")
        self.assertContains(
            response,
            "Vulekamali is a project by the South African National Treasury and Imali Yethu",
        )
        self.assertContains(response, "Important notice")

    def test_departments_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/2019-20/departments")

        self.assertContains(response, "Department Budgets for 2019-20 - vulekamali")

    def test_department_detail_page(self):
        """Test that it loads and that some text is present"""
        with patch(
            "budgetportal.views.DepartmentSubprogrammes.get_openspending_api",
            MagicMock(return_value=self.mock_openspending_api),
        ):
            c = Client()
            response = c.get("/2019-20/national/departments/the-presidency/")

        self.assertContains(
            response, "The Presidency budget data for the 2019-20 financial year"
        )
        self.assertContains(response, "Budget (Main appropriation) 2019-20")

    def test_department_preview_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/2019-20/previews/national/south-africa/social-development")

        self.assertContains(response, '<div data-webapp="preview-pages"')
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
        response = c.get("/learning-resources", follow=True)

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
        response = c.get("/learning-resources/resources")
        content = response.content
        self.assertContains(response, "The Budget Process and Public Participation")

    def test_glossary_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/learning-resources/glossary")

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

        self.assertContains(response, 'data-webapp="focus-areas-preview"')

    def test_dataset_page(self):
        """Test that it loads and that some text is present"""
        CategoryGuide.objects.all().delete()
        c = Client()
        response = c.get("/datasets/test-slug/test-2018-19")

        self.assertContains(response, "<title>Test 2018/19 - vulekamali</title>")
        self.assertContains(response, '<a href="/datasets/test-slug">test-slug</a>')
        self.assertContains(response, "Test 2018/19")
        self.assertNotContains(response, "Learn more")

    def test_dataset_page_when_category_guide_points_to_guide(self):
        """Test that it loads and that some text is present"""
        category_guide = CategoryGuide.objects.exclude(guide_page=None).first()
        self.assertIsNotNone(category_guide)

        category_guide.category_slug = "test-slug"
        category_guide.save()

        c = Client()
        response = c.get("/datasets/test-slug/test-2018-19")

        self.assertContains(response, "<title>Test 2018/19 - vulekamali</title>")
        self.assertContains(response, '<a href="/datasets/test-slug">test-slug</a>')
        self.assertContains(response, "Test 2018/19")
        self.assertContains(response, "Learn more")
        self.assertContains(response, 'href="{}"'.format(category_guide.guide_page.url))

    def test_dataset_page_when_category_guide_points_to_external_url(self):
        """Test that it loads and that some text is present"""
        category_guide = CategoryGuide.objects.filter(guide_page=None).first()
        self.assertIsNotNone(category_guide)

        category_guide.category_slug = "test-slug"
        category_guide.save()

        c = Client()
        response = c.get("/datasets/test-slug/test-2018-19")

        self.assertContains(response, "<title>Test 2018/19 - vulekamali</title>")
        self.assertContains(response, '<a href="/datasets/test-slug">test-slug</a>')
        self.assertContains(response, "Test 2018/19")
        self.assertContains(response, "Learn more")
        self.assertContains(response, 'href="{}"'.format(category_guide.external_url))

    def test_infrastructure_projects_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get("/infrastructure-projects")

        self.assertContains(
            response,
            '<div data-webapp="infrastructure-pages" class="infrastructure-projects"></div>',
        )
