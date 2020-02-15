from budgetportal.import_export_admin import (
    CustomGovernmentWidget,
    CustomIsVotePrimaryWidget,
)
from budgetportal.models import Department, FinancialYear, Government, Sphere
from django.core.exceptions import ValidationError
from django.test import TestCase


class CustomIsVotePrimaryWidgetTest(TestCase):
    def setUp(self):
        self.widget = CustomIsVotePrimaryWidget()

    def test_clean(self):
        self.assertTrue(self.widget.clean(""))
        self.assertTrue(self.widget.clean(None))
        self.assertTrue(self.widget.clean("true"))
        self.assertTrue(self.widget.clean("True"))
        self.assertFalse(self.widget.clean("false"))
        self.assertFalse(self.widget.clean("False"))
        self.assertFalse(self.widget.clean("0"))
        self.assertFalse(self.widget.clean("1"))

    def test_render(self):
        self.assertEqual(self.widget.render(True), "True")
        self.assertEqual(self.widget.render(False), "False")


class CustomGovernmentWidgetTest(TestCase):
    def setUp(self):
        self.widget = CustomGovernmentWidget()
        self.year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=self.year, name="A sphere")
        self.government = Government.objects.create(
            sphere=self.sphere, name="A government"
        )

    def test_set_sphere(self):
        self.widget.set_sphere(self.sphere.id)
        with self.assertRaises(ValidationError):
            self.widget.set_sphere(self.sphere.id + 1)

    def test_clean(self):
        self.widget.set_sphere(self.sphere.id)
        self.assertEqual(self.government, self.widget.clean(self.government.name))
        self.assertEqual(self.government, self.widget.clean(self.government.slug))
        with self.assertRaises(ValidationError):
            self.widget.clean("another value")

        another_sphere = Sphere.objects.create(
            financial_year=self.year, name="Another sphere"
        )
        self.widget.set_sphere(another_sphere.id)
        with self.assertRaises(ValidationError):
            self.widget.clean(self.government.slug)

    def test_render(self):
        self.widget.set_sphere(self.sphere.id)
        self.assertEqual(self.government.name, self.widget.render(self.government))
