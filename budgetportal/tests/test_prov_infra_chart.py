import json

from django.test import TestCase

from budgetportal.models import (
    ProvInfraProjectSnapshot,
    ProvInfraProject,
    IRMSnapshot,
    FinancialYear,
    Quarter,
)
from budgetportal.prov_infra_project.charts import time_series_data


class Q1UpdateTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q1 = Quarter.objects.create(number=1)
        irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q1, date_taken="2030-06-30"
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )

    def test_q1_updated_after_q2_snapshot_inserted(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 1)

        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 10)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)

        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=11,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 11)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 211)


class Q1Q2UpdateTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q1 = Quarter.objects.create(number=1)
        irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q1, date_taken="2030-06-30"
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=11,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )

    def test_q1_q2_updated_after_q3_snapshot_inserted(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 11)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 211)

        self.assertEqual(snapshots_data[1]["total_spent_in_quarter"], 20)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 231)

        q3 = Quarter.objects.create(number=3)
        irm_snapshot_3 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q3, date_taken="2030-12-31"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_3,
            project=self.project,
            actual_expenditure_q1=12,
            actual_expenditure_q2=21,
            actual_expenditure_q3=30,
            expenditure_from_previous_years_total=200,
        )
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 3)

        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 12)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 212)

        self.assertEqual(snapshots_data[1]["total_spent_in_quarter"], 21)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 233)


class NullQuarterlySpendTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q1 = Quarter.objects.create(number=1)
        irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q1, date_taken="2030-06-30"
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=None,
            expenditure_from_previous_years_total=200,
        )
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=None,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )

    def test_total_spends_are_none(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["total_spent_to_date"], None)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], None)


class NullQuarterlySpendSecondTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q1 = Quarter.objects.create(number=1)
        irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q1, date_taken="2030-06-30"
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=None,
            expenditure_from_previous_years_total=200,
        )

    def test_second_total_spend_is_none(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 10)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)
        self.assertEqual(snapshots_data[1]["total_spent_in_quarter"], None)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], None)


class LatestValueTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q1 = Quarter.objects.create(number=1)
        irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q1, date_taken="2030-06-30"
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=100,
        )

    def test_correct_value_used_for_previous_total(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 1)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 110)

        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 230)


class NullExpenditureFromPreviousFinYearsTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=None,
        )

    def test_total_spends_are_none(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["total_spent_to_date"], None)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], None)


class EmitMissingQuartersFirstTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_two_snapshots_emitted(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["financial_year_label"], "2030-31")
        self.assertEqual(snapshots_data[0]["date"], "2030-06-30")
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[1]["date"], "2030-09-30")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")

        quarters = [x["quarter_label"] for x in snapshots_data]
        self.assertNotIn("END Q3", quarters)
        self.assertNotIn("END Q4", quarters)


class EmitMissingQuartersSecondTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year_1 = FinancialYear.objects.create(slug="2018-19")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year_1, quarter=q2, date_taken="2018-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project
        )
        self.fin_year_2 = FinancialYear.objects.create(slug="2019-20")
        q4 = Quarter.objects.create(number=4)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year_2, quarter=q4, date_taken="2020-03-31"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_six_snapshots_emitted(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 6)

        self.assertEqual(snapshots_data[0]["financial_year_label"], "2018-19")
        self.assertEqual(snapshots_data[0]["date"], "2018-06-30")
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[1]["date"], "2018-09-30")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")

        self.assertEqual(snapshots_data[2]["financial_year_label"], "2019-20")
        self.assertEqual(snapshots_data[2]["date"], "2019-06-30")
        self.assertEqual(snapshots_data[2]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[3]["date"], "2019-09-30")
        self.assertEqual(snapshots_data[3]["quarter_label"], "END Q2")
        self.assertEqual(snapshots_data[4]["date"], "2019-12-31")
        self.assertEqual(snapshots_data[4]["quarter_label"], "END Q3")
        self.assertEqual(snapshots_data[5]["date"], "2020-03-31")
        self.assertEqual(snapshots_data[5]["quarter_label"], "END Q4")


class FinancialYearLabelTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_label_is_assigned_to_q1(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[0]["financial_year_label"], "2030-31")

    def test_label_is_empty_for_q2(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")
        self.assertEqual(snapshots_data[1]["financial_year_label"], "")


class QuarterLabelTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q4 = Quarter.objects.create(number=4)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q4, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_label_is_correct(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 4)

        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")
        self.assertEqual(snapshots_data[2]["quarter_label"], "END Q3")
        self.assertEqual(snapshots_data[3]["quarter_label"], "END Q4")


class TotalEstimatedProjectCostTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project, total_project_cost=100
        )

    def test_total_project_cost_is_null(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["total_estimated_project_cost"], None)

    def test_total_project_cost_assigned_correctly(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)
        self.assertEqual(snapshots_data[1]["total_estimated_project_cost"], 100)


class StatusTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2, project=self.project, status="Tender"
        )

    def test_status_is_null(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        self.assertEqual(snapshots_data[0]["status"], None)

    def test_status_assigned_correctly(self):
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)
        self.assertEqual(snapshots_data[1]["status"], "Tender")