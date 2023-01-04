from budgetportal.models import (
    NATIONAL_SLUG,
    PROVINCIAL_SLUG,
    Department,
    FinancialYear,
    Government,
    InYearMonitoringResourceLink,
    PerformanceResourceLink,
    ProcurementResourceLink,
    Sphere,
)
from django.test import Client, TestCase
from mock import MagicMock, patch


class DepartmentPageTestCase(TestCase):
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

        models_ckan_patch = patch("budgetportal.models.government.ckan")
        ModelsCKANMockClass = models_ckan_patch.start()
        ModelsCKANMockClass.action.package_search.return_value = {"results": []}
        self.addCleanup(models_ckan_patch.stop)

        datasets_ckan_patch = patch("budgetportal.datasets.ckan")
        DatasetsCKANMockClass = datasets_ckan_patch.start()
        DatasetsCKANMockClass.action.package_search.return_value = {"results": []}
        self.addCleanup(datasets_ckan_patch.stop)

        dataset_patch = patch(
            "budgetportal.datasets.Dataset.get_latest_cpi_resource",
            return_value=("2018-19", "5b315ff0-55e9-4ba8-b88c-2d70093bfe9d"),
        )
        dataset_patch.start()
        self.addCleanup(dataset_patch.stop)

    def test_no_resource_links(self):
        """Test that the page loads with no resource links existing"""
        ProcurementResourceLink.objects.all().delete()
        PerformanceResourceLink.objects.all().delete()
        InYearMonitoringResourceLink.objects.all().delete()

        c = Client()
        response = c.get("/2018-19/national/departments/the-presidency/")

        self.assertContains(
            response, "The Presidency budget data for the 2018-19 financial year"
        )
        self.assertContains(response, "Implementation data coming soon.")
        self.assertNotContains(response, "Procurement resources")
        self.assertNotContains(response, "Performance resources")
        self.assertNotContains(response, "In-year monitoring resources")

    def test_basic_links(self):
        ProcurementResourceLink.objects.create(
            title="a procurement link", url="a.com", description="abc"
        )
        PerformanceResourceLink.objects.create(
            title="a performance link", url="a.com", description="abc"
        )
        InYearMonitoringResourceLink.objects.create(
            title="an in-year link", url="a.com", description="abc"
        )

        c = Client()
        response = c.get("/2018-19/national/departments/the-presidency/")

        self.assertContains(
            response, "The Presidency budget data for the 2018-19 financial year"
        )
        self.assertNotContains(response, "Implementation data coming soon.")
        self.assertContains(response, "Procurement resources")
        self.assertContains(response, "a procurement link")
        self.assertContains(response, "Performance monitoring resources")
        self.assertContains(response, "a performance link")
        self.assertContains(response, "In-year monitoring resources")
        self.assertContains(response, "an in-year link")

    def test_sphere_specific_links(self):
        ProcurementResourceLink.objects.create(
            title="a national link",
            url="a.com",
            description="abc",
            sphere_slug=NATIONAL_SLUG,
        )
        PerformanceResourceLink.objects.create(
            title="a provincial link",
            url="a.com",
            description="abc",
            sphere_slug=PROVINCIAL_SLUG,
        )
        InYearMonitoringResourceLink.objects.create(
            title="an all-sphere link",
            url="a.com",
            description="abc",
            sphere_slug="all",
        )

        c = Client()
        response = c.get("/2018-19/national/departments/the-presidency/")

        self.assertContains(
            response, "The Presidency budget data for the 2018-19 financial year"
        )
        self.assertContains(response, "a national link")
        self.assertNotContains(response, "a provincial link")
        self.assertContains(response, "an all-sphere link")

    def test_missing_budget_dataset(self):
        c = Client()
        response = c.get("/2018-19/national/departments/the-presidency/")

        self.assertContains(response, "Data not available")
        self.assertNotContains(response, "Budget (Main appropriation) 2019-20")

    def test_budget_dataset_available(self):
        # mock get dataset to return mock dataset which includes opn_spending _api mocks
        mock_dataset = MagicMock()
        mock_dataset.get_openspending_api.return_value = self.mock_openspending_api
        with patch(
            "budgetportal.views.DepartmentSubprogrammes.get_dataset",
            MagicMock(return_value=mock_dataset),
        ):
            c = Client()
            response = c.get("/2018-19/national/departments/the-presidency/")

        self.assertContains(response, "Budget (Main appropriation) 2018-19")    
        self.assertNotContains(response, "Data not available")
        self.assertContains(response, "/2018-19/national/departments/the-presidency/viz/subprog-treemap")
