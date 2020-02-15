from budgetportal.import_export_admin import (DepartmentInstanceLoader,
                                              DepartmentResource)
from budgetportal.models import Department, FinancialYear, Government, Sphere
from django.core.exceptions import ValidationError
from django.test import TestCase
from import_export import instance_loaders, resources
from tablib import Dataset


class DepartmentInstanceLoaderTest(TestCase):
    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=self.year, name="A sphere")
        self.government = Government.objects.create(
            sphere=self.sphere, name="A government"
        )
        self.department = Department.objects.create(
            government=self.government,
            name="Department Name",
            vote_number=1,
            is_vote_primary=False,
            intro="Intro",
        )

        self.resource = DepartmentResource(sphere=self.sphere.id)
        fields = ["government", "department_name", "is_vote_primary", "vote_number"]
        self.dataset = Dataset(headers=fields)

    def test_get_instance_by_name(self):
        row = [
            self.government.name,
            self.department.name,
            "False",
            self.department.vote_number,
        ]
        self.dataset.append(row)
        self.instance_loader = DepartmentInstanceLoader(self.resource, self.dataset)

        instance = self.instance_loader.get_instance(self.dataset.dict[0])
        self.assertEquals(self.department, instance)

    def test_get_instance_by_slug(self):
        row = [
            self.government.name,
            self.department.name.upper(),
            "False",
            self.department.vote_number,
        ]
        self.dataset.append(row)
        self.instance_loader = DepartmentInstanceLoader(self.resource, self.dataset)

        instance = self.instance_loader.get_instance(self.dataset.dict[0])
        self.assertEquals(self.department, instance)

    def test_get_instance_by_vote_number(self):
        row = [self.government.name, "Different department name", "True", 1]
        self.dataset.append(row)
        self.instance_loader = DepartmentInstanceLoader(self.resource, self.dataset)

        instance = self.instance_loader.get_instance(self.dataset.dict[0])
        self.assertEquals(self.department, instance)

    def test_get_non_existent_instance(self):
        row = [self.government.name, "Different department name", "False", 1]
        self.dataset.append(row)
        self.instance_loader = DepartmentInstanceLoader(self.resource, self.dataset)

        instance = self.instance_loader.get_instance(self.dataset.dict[0])
        self.assertIsNone(instance)
