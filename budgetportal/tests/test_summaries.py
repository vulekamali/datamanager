"""
Tests of budgetportal.summaries
"""


import json

from budgetportal.models.gov_structure import (
    Department,
    FinancialYear,
    Government,
    Sphere,
)
from budgetportal.openspending import BabbageFiscalDataset
from budgetportal.summaries import (
    get_consolidated_expenditure_treemap,
    get_focus_area_preview,
    get_preview_page,
)
from django.test import TestCase
from mock import MagicMock, Mock, patch

with open("budgetportal/tests/test_data/consolidated_treemap.json", "r") as f:
    CONSOLIDATED_MOCK_DATA = json.load(f)

with open(
    "budgetportal/tests/test_data/test_summaries_focus_area_pages_provincial.json", "r"
) as f:
    FOCUS_AREA_PROVINCIAL_MOCK_DATA = json.load(f)

with open(
    "budgetportal/tests/test_data/test_summaries_focus_area_pages_national.json", "r"
) as f:
    FOCUS_AREA_NATIONAL_MOCK_DATA = json.load(f)

with open(
    "budgetportal/tests/test_data/test_summaries_focus_area_pages_national_subprogrammes.json",
    "r",
) as f:
    FOCUS_AREA_NATIONAL_SUBPROGRAMMES_MOCK_DATA = json.load(f)

with open(
    "budgetportal/tests/test_data/test_national_department_preview.json", "r"
) as f:
    NATIONAL_DEPARTMENT_PREVIEW_MOCK_DATA = json.load(f)


class ConsolidatedTreemapTestCase(TestCase):
    """ Unit tests for the consolidated treemap function(s) """

    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2019-20")

        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_adjustment_kind_ref = Mock(
            return_value="adjustment_kind_ref"
        )
        self.mock_openspending_api.aggregate = Mock(
            return_value={"cells": CONSOLIDATED_MOCK_DATA["complete"]}
        )
        self.mock_openspending_api.get_function_ref = Mock(
            return_value="function_group.function_group"
        )
        self.mock_openspending_api.get_year_ref = Mock(
            return_value="function_group.function_group"
        )
        self.mock_openspending_api.get_financial_year_ref = Mock(
            return_value="financial_year.financial_year"
        )
        self.mock_dataset = Mock()
        self.mock_dataset.get_openspending_api = Mock(
            return_value=self.mock_openspending_api
        )

    @patch("budgetportal.summaries.get_consolidated_expenditure_budget_dataset")
    def test_complete_data(self, mock_get_dataset):
        mock_get_dataset.return_value = self.mock_dataset

        result = get_consolidated_expenditure_treemap(self.year)
        data = result["data"]
        self.assertEqual(len(data), 2)
        data_keys = data.keys()
        self.assertIn("items", data_keys)
        self.assertIn("total", data_keys)
        expenditure_keys = data["items"][0].keys()
        self.assertIn("name", expenditure_keys)
        self.assertIn("amount", expenditure_keys)
        self.assertIn("percentage", expenditure_keys)
        self.assertIn("id", expenditure_keys)
        self.assertIn("url", expenditure_keys)


class FocusAreaPagesTestCase(TestCase):
    """ Integration test focus area page data generation """

    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2019-20")
        self.year.save()
        national = Sphere(financial_year=self.year, name="national")
        national.save()
        provincial = Sphere(financial_year=self.year, name="provincial")
        provincial.save()
        southafrica = Government(sphere=national, name="South Africa")
        southafrica.save()
        province = Government(sphere=provincial, name="Test Province 1")
        province.save()
        Department(
            government=southafrica,
            name="TP1 National Test Dept 2",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        ).save()
        Department(
            government=province,
            name="TP1 Provincial Test Dept 2",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        ).save()

        self.mock_dataset = Mock()
        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_geo_ref = Mock(
            return_value="geo_source.government"
        )
        self.mock_openspending_api.get_function_ref = Mock(
            return_value="function_group.function_group"
        )
        self.mock_openspending_api.get_year_ref = Mock(
            return_value="function_group.function_group"
        )
        self.mock_openspending_api.get_financial_year_ref = Mock(
            return_value="financial_year.financial_year"
        )
        self.mock_openspending_api.get_department_name_ref = Mock(
            return_value="vote_number.department"
        )
        self.mock_openspending_api.get_subprogramme_name_ref = Mock(
            return_value="subprogramme.subprogramme"
        )
        self.mock_dataset.get_openspending_api = Mock(
            return_value=self.mock_openspending_api
        )

        def mock_get_focus_area_data(__, sphere):
            if sphere == "provincial":
                cells = FOCUS_AREA_PROVINCIAL_MOCK_DATA
            elif sphere == "national":
                cells = FOCUS_AREA_NATIONAL_MOCK_DATA
            return cells, self.mock_openspending_api

        self.mock_get_focus_area_data = mock_get_focus_area_data

    @patch("budgetportal.summaries.get_prov_eq_share")
    @patch("budgetportal.summaries.get_focus_area_data")
    def test_get_focus_area_preview(
        self, mock_get_focus_area_data, mock_get_prov_eq_share
    ):
        mock_get_focus_area_data.side_effect = self.mock_get_focus_area_data
        mock_get_prov_eq_share.return_value = ("untested", 123)

        result = get_focus_area_preview(self.year)
        focus_areas = result["data"]["items"]
        fg1 = [f for f in focus_areas if f["slug"] == "test-fg-1"][0]
        fg2 = [f for f in focus_areas if f["slug"] == "test-fg-2"][0]

        self.assertEqual("Test FG 1", fg1["title"])
        self.assertEqual("Test FG 2", fg2["title"])

        self.assertEqual(6, len(fg1["national"]["data"]))
        self.assertEqual(6, len(fg1["provincial"]["data"]))

        nat_dept_data = [
            dept
            for dept in fg1["national"]["data"]
            if dept["title"] == "TP1 National Test Dept 2"
        ][0]
        self.assertTrue(nat_dept_data["slug"] in nat_dept_data["url"])
        self.assertTrue("2019-20" in nat_dept_data["url"])

        prov_dept_data = [
            dept
            for dept in fg1["provincial"]["data"]
            if dept["name"] == "TP1 Provincial Test Dept 2"
        ][0]
        self.assertTrue(prov_dept_data["slug"] in prov_dept_data["url"])
        self.assertTrue("2019-20" in prov_dept_data["url"])


class NationalDepartmentPreviewTestCase(TestCase):
    """ Unit tests for the national department preview department function. """

    def setUp(self):
        self.mock_data = NATIONAL_DEPARTMENT_PREVIEW_MOCK_DATA
        year = FinancialYear.objects.create(slug="2019-20")
        sphere = Sphere.objects.create(financial_year=year, name="national")
        government = Government.objects.create(sphere=sphere, name="South Africa")
        self.department = Department(
            government=government,
            name="Fake",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_adjustment_kind_ref = Mock(
            return_value="adjustment_kind_ref"
        )
        self.mock_openspending_api.get_phase_ref = Mock(
            return_value="budget_phase.budget_phase"
        )
        self.mock_openspending_api.get_programme_name_ref = Mock(
            return_value="programme_number.programme"
        )
        self.mock_openspending_api.get_department_name_ref = Mock(
            return_value="vote_number.department"
        )
        self.mock_openspending_api.get_geo_ref = Mock(
            return_value="geo_source.government"
        )
        self.mock_openspending_api.get_function_ref = Mock(
            return_value="function_group_1.function_group_1"
        )
        self.mock_openspending_api.get_financial_year_ref = Mock(
            return_value="financial_year.financial_year"
        )
        self.mock_openspending_api.aggregate = Mock(
            return_value={"cells": self.mock_data["programmes"]}
        )
        self.mock_openspending_api.filter_by_ref_exclusion = Mock(
            return_value=self.mock_data["programmes"]
        )
        self.mock_openspending_api.aggregate_url = Mock
        self.mock_dataset = Mock()
        self.mock_dataset.get_openspending_api = Mock(
            return_value=self.mock_openspending_api
        )

        vote_number = 1
        for mock_object in self.mock_data["departments"]:
            Department.objects.create(
                government=government,
                is_vote_primary=True,
                name=mock_object["vote_number.department"],
                vote_number=vote_number,
            )
            vote_number += 1

    @patch(
        "budgetportal.models.Department.get_all_budget_totals_by_year_and_phase",
        return_value=MagicMock(),
    )
    @patch("budgetportal.summaries.get_expenditure_time_series_dataset")
    def test_complete_data(self, mock_get_dataset, total_budgets_mock):
        self.mock_openspending_api.aggregate_by_refs = (
            BabbageFiscalDataset.aggregate_by_refs
        )
        mock_get_dataset.return_value = self.mock_dataset

        result = get_preview_page(
            financial_year_id="2019-20",
            phase_slug="original",
            government_slug="south-africa",
            sphere_slug="national",
        )
        data = result["data"]
        self.assertEqual(len(data), 1)
        data_keys = data.keys()
        self.assertIn("items", data_keys)
        expenditure_keys = data["items"][0].keys()
        self.assertIn("title", expenditure_keys)
        self.assertIn("description", expenditure_keys)
        self.assertIn("percentage_of_budget", expenditure_keys)
        self.assertIn("programmes", expenditure_keys)
        self.assertIn("slug", expenditure_keys)
        self.assertIn("focus_areas", expenditure_keys)

        self.assertEqual(
            data["items"][0]["focus_areas"][0]["slug"], "economic-development"
        )
