"""
Tests of models.Department
"""

from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)
from django.test import TestCase
from mock import Mock


class AdjustedBudgetMissingTestCase(TestCase):
    """Unit tests of adjusted budget data summary for a department"""
    def setUp(self):
        year = FinancialYear(slug="2030-31")
        sphere = Sphere(financial_year=year, name="A sphere")
        government = Government(sphere=sphere, name="A government")
        self.department = Department(
            government=government,
            name="Fake",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        self.department.get_adjusted_estimates_expenditure_dataset = Mock(return_value=None)

    def test_missing_dataset(self):
        self.assertEqual(self.department.get_adjusted_budget_summary(), None)
