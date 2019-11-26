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


class DateQuarterMatchTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2019-20")
        q4 = Quarter.objects.create(number=4)
        irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q4, date_taken="2020-03-31"
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot,
            project=self.project,
            estimated_construction_start_date="2019-01-01",
            estimated_construction_end_date="2021-12-31",
        )

    def test_dates_are_end_of_quarters(self):
        """Test that all dates are end day of a quarter"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 4)

        # Q1->06-30, Q2->09-30, Q3->12-31, Q4->03-31
        self.assertEqual(snapshots_data[0]["date"], "2019-06-30")
        self.assertEqual(snapshots_data[1]["date"], "2019-09-30")
        self.assertEqual(snapshots_data[2]["date"], "2019-12-31")
        self.assertEqual(snapshots_data[3]["date"], "2020-03-31")

    def test_dates_match_with_quarters(self):
        """Test that dates and quarter_labels match"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 4)

        # Q1->06-30, Q2->09-30, Q3->12-31, Q4->03-31
        self.assertEqual(snapshots_data[0]["date"], "2019-06-30")
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[1]["date"], "2019-09-30")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")
        self.assertEqual(snapshots_data[2]["date"], "2019-12-31")
        self.assertEqual(snapshots_data[2]["quarter_label"], "END Q3")
        self.assertEqual(snapshots_data[3]["date"], "2020-03-31")
        self.assertEqual(snapshots_data[3]["quarter_label"], "END Q4")


class Q1UpdateTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q1 = Quarter.objects.create(number=1)
        irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q1, date_taken="2030-06-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )

    def test_q1_updated_after_q2_snapshot_inserted(self):
        """Test that Q1 is updated correctly when Q2 inserted"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 1)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 10)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)

        # Create Q2 snapshot
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
        # Recreate the chart data
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
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
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )
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

    def test_q1_q2_updated_after_q3_snapshot_inserted(self):
        """Test that Q1 and Q2 are updated correctly when Q3 inserted"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 11)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 211)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["total_spent_in_quarter"], 20)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 231)

        # Create Q3 snapshot
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
        # Recreate the chart data
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 3)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 12)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 212)

        # Check Q2 values
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
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=None,
            expenditure_from_previous_years_total=200,
        )
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=None,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )

    def test_total_spends_are_none(self):
        """Test that total spends are none because of actual_expenditure_q1"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check total_spent_to_date values for Q1 and Q2
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
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=None,
            expenditure_from_previous_years_total=200,
        )

    def test_second_total_spend_is_none(self):
        """Test that Q2 total values are none because of actual_expenditure_q2"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 10)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)

        # Check Q2 values
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
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=100,
        )

    def test_correct_value_used_for_previous_total(self):
        """
        Test that Q2's expenditure_from_previous_years_total changes total_spent of Q1.
        """
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 1)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 110)

        # Create Q2 Snapshot
        q2 = Quarter.objects.create(number=2)
        irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )
        # Recreate the chart data
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check total_spent_to_date values for Q1 and Q2
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
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=None,
        )

    def test_total_spends_are_none(self):
        """Test that Q1 and Q2 total_spent values when expenditure_
        from_previous_years_total is empty."""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check total_spent_to_date values for Q1 and Q2
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], None)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], None)


class EmitMissingQuartersTestCase(TestCase):
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
        """Test that Q2 created 2 items"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["financial_year_label"], "2030-31")
        self.assertEqual(snapshots_data[0]["date"], "2030-06-30")
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["date"], "2030-09-30")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")


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
        """Test that 2018 Q2 created 2, and 2019 Q4 created 4 items"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 6)

        # Check 2018's Q1 and Q2 in a row
        self.assertEqual(snapshots_data[0]["financial_year_label"], "2018-19")
        self.assertEqual(snapshots_data[0]["date"], "2018-06-30")
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[1]["date"], "2018-09-30")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")

        # Check 2019's Q1, Q2, Q3 and Q4 in a row
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
        """Test that financial year label is correctly assigned for Q1"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[0]["financial_year_label"], "2030-31")

    def test_label_is_empty_for_q2(self):
        """Test that financial year label is empty for quarters except Q1"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q2 values
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
        """Test that quarter labels start with 'END Q' and ends with (1,2,3,4)"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 4)

        # Check quarter label texts for all quarters
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
        """Test that total project cost for Q1 (which created by Q2) is Null"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_estimated_project_cost"], None)

    def test_total_project_cost_assigned_correctly(self):
        """Test that total project cost for Q2 is 100"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q2 values
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
        """Test that status for Q1 (which created by Q2) is Null"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["status"], None)

    def test_status_assigned_correctly(self):
        """Test that status for Q2 is Tender"""
        snapshots_data = json.loads(time_series_data(self.project))
        snapshots_data = snapshots_data[u"snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["status"], "Tender")


class EventsTestCase(TestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        q2 = Quarter.objects.create(number=2)
        irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q2, date_taken="2030-09-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot,
            project=self.project,
            estimated_construction_start_date="2030-01-01",
            estimated_construction_end_date="2032-12-31",
        )

    def test_events_assigned_correctly(self):
        """Test that estimated constructions dates are assigned correctly"""
        events_data = json.loads(time_series_data(self.project))
        events_data = events_data[u"events"]
        self.assertEqual(len(events_data), 2)

        # Estimated construction start date
        self.assertEqual(events_data[0]["date"], "2030-01-01")
        # Estimated construction end date
        self.assertEqual(events_data[1]["date"], "2032-12-31")

    def test_events_when_latest_snapshot_has_empty_dates(self):
        """Test that dates are taken from Q2 instead of Q3"""
        q3 = Quarter.objects.create(number=3)
        irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=q3, date_taken="2030-09-30"
        )
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot, project=self.project
        )
        events_data = json.loads(time_series_data(self.project))
        events_data = events_data[u"events"]
        self.assertEqual(len(events_data), 2)

        # Estimated construction start date
        self.assertEqual(events_data[0]["date"], "2030-01-01")
        # Estimated construction end date
        self.assertEqual(events_data[1]["date"], "2032-12-31")
