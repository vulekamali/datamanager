import json

from budgetportal.infra_projects.charts import time_series_data
from budgetportal.json_encoder import JSONEncoder
from budgetportal.models import (
    FinancialYear,
    InfraProject,
    InfraProjectSnapshot,
    IRMSnapshot,
    Quarter,
    Sphere,
)
from django.test import TestCase


class DateQuarterMatchTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2019-20")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q4 = Quarter(number=4)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q4)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot,
            project=self.project,
            estimated_construction_start_date="2019-01-01",
            estimated_construction_end_date="2021-12-31",
        )

    def test_dates_are_end_of_quarters(self):
        """Test that all dates are end day of a quarter"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 4)

        # Q1->06-30, Q2->09-30, Q3->12-31, Q4->03-31
        self.assertEqual(snapshots_data[0]["date"], "2019-06-30")
        self.assertEqual(snapshots_data[1]["date"], "2019-09-30")
        self.assertEqual(snapshots_data[2]["date"], "2019-12-31")
        self.assertEqual(snapshots_data[3]["date"], "2020-03-31")

    def test_dates_match_with_quarters(self):
        """Test that dates and quarter_labels match"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
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


class TotalEstimatedProjectCostTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot,
            project=self.project,
            estimated_total_project_cost=100,
        )

    def test_estimated_total_project_cost_is_null(self):
        """Test that total project cost for Q1 (which created by Q2 snapshot) is Null"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_estimated_project_cost"], None)

    def test_estimated_total_project_cost_assigned_correctly(self):
        """Test that total project cost for Q2 is 100"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["total_estimated_project_cost"], 100)


class StatusTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot, project=self.project, status="Tender"
        )

    def test_status_is_null(self):
        """Test that status for Q1 (which created by Q2 snapshot) is Null"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["status"], None)

    def test_status_assigned_correctly(self):
        """Test that status for Q2 is Tender"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["status"], "Tender")


class Q1UpdateTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q1 = Quarter(number=1)
        irm_snapshot_1 = IRMSnapshot(sphere=self.sphere, quarter=q1)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )

    def test_q1_updated_after_q2_snapshot_inserted(self):
        """Test that Q1 values are updated correctly when Q2 snapshot is added"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 1)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 10)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)

        # Create Q2 snapshot
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot_2 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=11,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )
        # Recreate the chart data
        snapshots_data = time_series_data(
            [self.project_snapshot, self.project_snapshot_2]
        )
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 11)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 211)


class Q1Q2UpdateTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q1 = Quarter(number=1)
        irm_snapshot_1 = IRMSnapshot(sphere=self.sphere, quarter=q1)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=200,
        )
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot_2 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=11,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )

    def test_q1_q2_updated_after_q3_snapshot_inserted(self):
        """Test that Q1 and Q2 are updated correctly when Q3 inserted"""
        snapshots_data = time_series_data(
            [self.project_snapshot, self.project_snapshot_2]
        )
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 11)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 211)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["total_spent_in_quarter"], 20)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 231)

        # Create Q3 snapshot
        q3 = Quarter(number=3)
        irm_snapshot_3 = IRMSnapshot(sphere=self.sphere, quarter=q3)
        self.project_snapshot_3 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_3,
            project=self.project,
            actual_expenditure_q1=12,
            actual_expenditure_q2=21,
            actual_expenditure_q3=30,
            expenditure_from_previous_years_total=200,
        )
        # Recreate the chart data
        snapshots_data = time_series_data(
            [self.project_snapshot, self.project_snapshot_2, self.project_snapshot_3]
        )
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 3)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["total_spent_in_quarter"], 12)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 212)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["total_spent_in_quarter"], 21)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 233)


class NullQ2SubsequentNullSpendTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q3 = Quarter(number=3)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q3)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=None,
            actual_expenditure_q3=30,
            expenditure_from_previous_years_total=200,
        )

    def test_total_spends_are_correct(self):
        """Test that total spends are none because of actual_expenditure_q1"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 3)

        # Check total_spent_to_date values for Q1, Q2 and Q3
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], None)
        self.assertEqual(snapshots_data[2]["total_spent_to_date"], None)


class LatestValueTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q1 = Quarter(number=1)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q1)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot,
            project=self.project,
            actual_expenditure_q1=10,
            expenditure_from_previous_years_total=100,
        )

    def test_correct_value_used_for_previous_total(self):
        """
        Q2 snapshot's expenditure_from_previous_years_total updates total_spent of Q1 chart item.
        """
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 1)
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 110)

        # Create Q2 Snapshot
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot_2 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=200,
        )
        # Recreate the chart data
        snapshots_data = time_series_data(
            [self.project_snapshot, self.project_snapshot_2]
        )
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check total_spent_to_date values for Q1 and Q2
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], 210)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], 230)


class NullExpenditureFromPreviousFinYearsTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=10,
            actual_expenditure_q2=20,
            expenditure_from_previous_years_total=None,
        )

    def test_total_spends_are_none(self):
        """Test that Q1 and Q2 total_spent values when expenditure_
        from_previous_years_total is empty."""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check total_spent_to_date values for Q1 and Q2
        self.assertEqual(snapshots_data[0]["total_spent_to_date"], None)
        self.assertEqual(snapshots_data[1]["total_spent_to_date"], None)


class EmitMissingQuartersTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot, project=self.project
        )

    def test_two_snapshots_emitted(self):
        """Test that if the first snapshot is Q2, items are created for Q1 and Q2 but nothing later than Q2."""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
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
        self.project = InfraProject(IRM_project_id=1)
        fin_year_1 = FinancialYear(slug="2018-19")
        self.sphere_1 = Sphere(financial_year=fin_year_1, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere_1, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2, project=self.project
        )
        fin_year_2 = FinancialYear(slug="2019-20")
        self.sphere_2 = Sphere(financial_year=fin_year_2, name="Provincial")
        q4 = Quarter(number=4)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere_2, quarter=q4)
        self.project_snapshot_2 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_six_snapshots_emitted(self):
        """Test that 2018 Q2 created 2, and 2019 Q4 created 4 items"""
        snapshots_data = time_series_data(
            [self.project_snapshot, self.project_snapshot_2]
        )
        snapshots_data = snapshots_data["snapshots"]
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


class ComputeTotalSpentIn2YearsTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year_1 = FinancialYear(slug="2018-19")
        self.sphere_1 = Sphere(financial_year=fin_year_1, name="Provincial")
        q4 = Quarter(number=4)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere_1, quarter=q4)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=1,
            actual_expenditure_q2=2,
            actual_expenditure_q3=3,
            actual_expenditure_q4=4,
            expenditure_from_previous_years_total=100,
        )
        fin_year_2 = FinancialYear(slug="2019-20")
        self.sphere_2 = Sphere(financial_year=fin_year_2, name="Provincial")
        q1 = Quarter(number=1)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere_2, quarter=q1)
        self.project_snapshot_2 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            actual_expenditure_q1=50,
            expenditure_from_previous_years_total=200,
        )

    def test_total_spent_to_dates_are_correct(self):
        """Test that the second year's total_spent_to_date starts from the second
        year's total_from_previous_financial_years."""
        snapshots_data = time_series_data(
            [self.project_snapshot, self.project_snapshot_2]
        )
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 5)

        # Check that 2019 Q1 Snapshot's total_spent_to_date is correct
        self.assertNotEqual(snapshots_data[4]["total_spent_to_date"], 110)
        self.assertEqual(snapshots_data[4]["total_spent_to_date"], 250)


class FinancialYearLabelTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_label_is_assigned_to_q1(self):
        """Test that financial year label is correctly assigned for Q1"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q1 values
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[0]["financial_year_label"], "2030-31")

    def test_label_is_empty_for_q2(self):
        """Test that financial year label is empty for quarters except Q1"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 2)

        # Check Q2 values
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")
        self.assertEqual(snapshots_data[1]["financial_year_label"], "")


class QuarterLabelTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q4 = Quarter(number=4)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q4)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2, project=self.project
        )

    def test_label_is_correct(self):
        """Test that quarter labels start with 'END Q' and ends with (1,2,3,4)"""
        snapshots_data = time_series_data([self.project_snapshot])
        snapshots_data = snapshots_data["snapshots"]
        self.assertEqual(len(snapshots_data), 4)

        # Check quarter label texts for all quarters
        self.assertEqual(snapshots_data[0]["quarter_label"], "END Q1")
        self.assertEqual(snapshots_data[1]["quarter_label"], "END Q2")
        self.assertEqual(snapshots_data[2]["quarter_label"], "END Q3")
        self.assertEqual(snapshots_data[3]["quarter_label"], "END Q4")


class EventsTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot,
            project=self.project,
            start_date="2029-09-30",
            estimated_construction_start_date="2030-01-01",
            estimated_completion_date="2033-02-01",
            contracted_construction_end_date="2033-01-31",
            estimated_construction_end_date="2032-12-31",
        )

    def test_events_assigned_correctly(self):
        """Test that all dates are assigned correctly"""
        events_data = time_series_data([self.project_snapshot])
        events_data = events_data["events"]
        self.assertEqual(len(events_data), 5)

        # Project Start Date
        self.assertEqual(events_data[0]["date"], "2029-09-30")
        # Estimated Construction Start Date
        self.assertEqual(events_data[1]["date"], "2030-01-01")
        # Estimated Completion Date
        self.assertEqual(events_data[2]["date"], "2033-02-01")
        # Contracted Construction End Date
        self.assertEqual(events_data[3]["date"], "2033-01-31")
        # Estimated Construction End Date
        self.assertEqual(events_data[4]["date"], "2032-12-31")

    def test_events_when_latest_snapshot_has_empty_dates(self):
        """Test that only not null values emitted to events"""
        q3 = Quarter(number=3)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q3)
        self.project_snapshot_2 = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2, project=self.project, start_date="2029-09-30"
        )
        events_data = time_series_data([self.project_snapshot, self.project_snapshot_2])
        events_data = events_data["events"]
        self.assertEqual(len(events_data), 1)

        # Project Start Date
        self.assertEqual(events_data[0]["date"], "2029-09-30")


class SerializeChartDataResultTestCase(TestCase):
    def setUp(self):
        self.project = InfraProject(IRM_project_id=1)
        fin_year = FinancialYear(slug="2030-31")
        self.sphere = Sphere(financial_year=fin_year, name="Provincial")
        q2 = Quarter(number=2)
        irm_snapshot_2 = IRMSnapshot(sphere=self.sphere, quarter=q2)
        self.project_snapshot = InfraProjectSnapshot(
            irm_snapshot=irm_snapshot_2, project=self.project, status="Tender"
        )

    def test_chart_data_can_be_serialized(self):
        """Test that it is possible to serialize and deserialize chart data"""
        original_chart_data = time_series_data([self.project_snapshot])
        serialized_data = json.dumps(original_chart_data, cls=JSONEncoder)
        converted_chart_data = json.loads(serialized_data)

        self.assertEqual(original_chart_data, converted_chart_data)
