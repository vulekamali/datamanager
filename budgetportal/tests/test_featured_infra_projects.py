import mock
from budgetportal.models import (
    MAPIT_POINT_API_URL,
    InfrastructureProjectPart,
)
from budgetportal.tests.helpers import WagtailHackLiveServerTestCase
from django.test import Client, TestCase


class ProjectedExpenditureTestCase(TestCase):
    """ Unit tests for get_projected_expenditure function """

    fixtures = ["test-infrastructure-pages-detail"]

    def setUp(self):
        self.project = InfrastructureProjectPart.objects.all().first()

    def test_success(self):
        projected_expenditure = self.project.calculate_projected_expenditure()
        self.assertEqual(projected_expenditure, 5688808000.0)


class CoordinatesTestCase(TestCase):
    """ Unit tests for parsing coordinates """

    def test_success_simple_format(self):
        raw_coord_string = "-26.378582,27.654933"
        cleaned_coord_object = InfrastructureProjectPart._parse_coordinate(
            raw_coord_string
        )
        self.assertEqual(
            cleaned_coord_object, {"latitude": -26.378582, "longitude": 27.654933}
        )

    def test_failure_int_raises_type_error(self):
        invalid_coordinate = 25
        self.assertRaises(
            TypeError, InfrastructureProjectPart._parse_coordinate, invalid_coordinate
        )

    def test_failure_list_raises_type_error(self):
        invalid_coordinate = [25, 23]
        self.assertRaises(
            TypeError, InfrastructureProjectPart._parse_coordinate, invalid_coordinate
        )

    def test_success_multiple_coordinates(self):
        raw_coordinate_string = "-26.378582,27.654933 and -22.111222,23.333444"
        coords = InfrastructureProjectPart.clean_coordinates(raw_coordinate_string)
        self.assertIn({"latitude": -26.378582, "longitude": 27.654933}, coords)
        self.assertIn({"latitude": -22.111222, "longitude": 23.333444}, coords)

    def test_empty_response_for_invalid_value(self):
        raw_coordinate_string = "test string with, no coords and"
        coords = InfrastructureProjectPart.clean_coordinates(raw_coordinate_string)
        self.assertEqual(coords, [])


class ExpenditureTestCase(TestCase):
    """ Unit tests for expenditure functions """

    fixtures = ["test-infrastructure-pages-detail"]

    def setUp(self):
        self.project = InfrastructureProjectPart.objects.all().first()

    def test_success_build_expenditure_item(self):
        expenditure_item = InfrastructureProjectPart._build_expenditure_item(
            self.project
        )
        self.assertEqual(
            expenditure_item,
            {
                "year": self.project.financial_year,
                "amount": self.project.amount_rands,
                "budget_phase": self.project.budget_phase,
            },
        )

    def test_success_build_complete_expenditure(self):
        complete_expenditure = self.project.build_complete_expenditure()
        self.assertIn(
            {
                "year": self.project.financial_year,
                "amount": self.project.amount_rands,
                "budget_phase": self.project.budget_phase,
            },
            complete_expenditure,
        )


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return None


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    if args[0] == MAPIT_POINT_API_URL.format(25.312526, -27.515232):
        return MockResponse({4288: {"name": "Fake Province 1"}}, 200)
    elif args[0] == MAPIT_POINT_API_URL.format(24.312526, -26.515232):
        return MockResponse({}, 200)
    elif args[0] == MAPIT_POINT_API_URL.format(29.45397, -31.45019):
        return MockResponse({4288: {"name": "Fake Province 3"}}, 200)
    elif args[0] == MAPIT_POINT_API_URL.format(25.443304, -33.399790):
        return MockResponse({4288: {"name": "Fake Province 4"}}, 200)
    elif args[0] == MAPIT_POINT_API_URL.format(15.443304, -30.399790):
        return MockResponse({4288: {"name": "Fake Province 5"}}, 200)
    return MockResponse(None, 404)


class ProvinceTestCase(TestCase):
    def setUp(self):
        self.test_coordinates_one = {"longitude": 25.312526, "latitude": -27.515232}
        self.test_coordinates_two = {"longitude": 24.312526, "latitude": -26.515232}

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_success_one_result(self, mock_get):
        province = InfrastructureProjectPart._get_province_from_coord(
            self.test_coordinates_one
        )
        self.assertEqual(province, "Fake Province 1")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_success_no_results(self, mock_get):
        province = InfrastructureProjectPart._get_province_from_coord(
            self.test_coordinates_two
        )
        self.assertEqual(province, None)

    def test_success_province_from_name(self):
        province = InfrastructureProjectPart._get_province_from_project_name(
            "Eastern Cape: A New Test"
        )
        self.assertEqual(province, "Eastern Cape")


empty_ckan_response = MockResponse({"result": {"records": []}}, 200)


class OverviewIntegrationTest(WagtailHackLiveServerTestCase):
    fixtures = ["test-infrastructure-pages-overview"]

    def setUp(self):
        self.standard_fake_project = InfrastructureProjectPart.objects.filter(
            project_name="Standard fake project"
        ).first()

    @mock.patch("requests.get", return_value=empty_ckan_response)
    def test_success_empty_projects(self, mock_get):
        """ Test that it exists and that the correct years are linked. """
        InfrastructureProjectPart.objects.all().delete()
        c = Client()
        response = c.get("/json/infrastructure-projects.json")
        content = response.json()

        self.assertEqual(content["projects"], [])
        self.assertEqual(content["dataset_url"], "/datasets/infrastructure-projects")
        self.assertEqual(
            content["description"],
            "National department Infrastructure projects in South Africa",
        )
        self.assertEqual(content["selected_tab"], "infrastructure-projects")
        self.assertEqual(content["slug"], "infrastructure-projects")
        self.assertEqual(content["title"], "Infrastructure Projects - vulekamali")

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_success_with_projects(self, mock_get):
        """ Test that it exists and that the correct years are linked. """
        c = Client()
        response = c.get("/json/infrastructure-projects.json")
        content = response.json()

        self.assertEqual(len(content["projects"]), 2)

        # First project (single coords, province)
        first_test_project = list(
            filter(lambda x: x["name"] == "Standard fake project", content["projects"])
        )[0]
        self.assertEqual(
            first_test_project["description"], "Typical project description"
        )
        self.assertEqual(
            first_test_project["detail"],
            "/infrastructure-projects/health-standard-fake-project",
        )
        self.assertEqual(first_test_project["infrastructure_type"], "fake type")

        self.assertIn(
            {"latitude": -31.45019, "longitude": 29.45397},
            first_test_project["coordinates"],
        )
        self.assertEqual(len(first_test_project["coordinates"]), 1)

        self.assertEqual(len(first_test_project["expenditure"]), 7)
        for item in self.standard_fake_project.build_complete_expenditure():
            self.assertIn(item, first_test_project["expenditure"])
        self.assertEqual(
            first_test_project["nature_of_investment"], "standard fake investment"
        )
        self.assertEqual(
            first_test_project["page_title"], "Standard fake project - vulekamali"
        )
        self.assertEqual(first_test_project["projected_budget"], 5688808000.0)
        self.assertIn("Fake province 1", first_test_project["provinces"])
        self.assertEqual(len(first_test_project["provinces"]), 1)
        self.assertEqual(
            first_test_project["slug"],
            "/infrastructure-projects/health-standard-fake-project",
        )
        self.assertEqual(first_test_project["stage"], "Fake stage")
        self.assertEqual(first_test_project["total_budget"], 9045389000)

        # Second project (multiple coords, provinces)
        second_test_project = list(
            filter(lambda x: x["name"] == "Fake project 2", content["projects"])
        )[0]
        self.assertIn(
            {"latitude": -33.399790, "longitude": 25.443304},
            second_test_project["coordinates"],
        )
        self.assertIn(
            {"latitude": -30.399790, "longitude": 15.443304},
            second_test_project["coordinates"],
        )
        self.assertEqual(len(second_test_project["coordinates"]), 2)
        self.assertIn("Fake province 2", second_test_project["provinces"])
        self.assertIn(" Fake province 3", second_test_project["provinces"])
        self.assertEqual(len(second_test_project["provinces"]), 2)


class DetailIntegrationTest(WagtailHackLiveServerTestCase):

    fixtures = ["test-infrastructure-pages-detail"]

    def setUp(self):
        self.project = InfrastructureProjectPart.objects.all().first()

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_success_with_projects(self, mock_get):
        """ Test that it exists and that the correct years are linked. """
        c = Client()
        response = c.get(
            "/json/infrastructure-projects/{}.json".format(self.project.project_slug)
        )
        content = response.json()["projects"][0]

        self.assertEqual(content["dataset_url"], "/datasets/infrastructure-projects")
        self.assertEqual(content["description"], self.project.project_description)
        self.assertEqual(
            content["infrastructure_type"], self.project.infrastructure_type
        )
        self.assertEqual(len(content["coordinates"]), 0)
        self.assertEqual(len(content["expenditure"]), 7)
        for item in self.project.build_complete_expenditure():
            self.assertIn(item, content["expenditure"])
        self.assertEqual(
            content["nature_of_investment"], self.project.nature_of_investment
        )
        self.assertEqual(
            content["page_title"], "{} - vulekamali".format(self.project.project_name)
        )
        self.assertEqual(
            content["projected_budget"], self.project.calculate_projected_expenditure()
        )
        self.assertEqual(len(content["provinces"]), 1)
        self.assertIn("", content["provinces"][0])
        self.assertEqual(
            content["slug"],
            "/infrastructure-projects/{}".format(self.project.project_slug),
        )
        self.assertEqual(content["stage"], self.project.current_project_stage)
        self.assertEqual(content["total_budget"], self.project.project_value_rands)
