from budgetportal.models import FinancialYear, Sphere, Government, Department, Programme
from django.core.management import call_command
from django.test import TestCase
from tempfile import NamedTemporaryFile
from io import StringIO
import yaml
from mock import Mock

# Hacky make sure we don't call out to openspending.
import requests

requests.get = Mock
requests.Session = Mock


class BasicPagesTestCase(TestCase):
    def setUp(self):
        year = FinancialYear.objects.create(slug="2030-31")

        # spheres
        national = Sphere.objects.create(financial_year=year, name="National")
        provincial = Sphere.objects.create(financial_year=year, name="Provincial")

        # governments
        self.fake_national_government = Government.objects.create(
            sphere=national, name="South Africa"
        )
        self.fake_provincial_government = Government.objects.create(
            sphere=provincial, name="Free State"
        )

    def test_load_departments_national(self):
        filename = "budgetportal/tests/test_data/test_management_commands_national_departments.csv"
        call_command("load_departments", "2030-31", "national", filename)

        presidency = Department.objects.get(
            government=self.fake_national_government, name="The Presidency"
        )
        self.assertEqual(presidency.vote_number, 1)
        self.assertTrue(presidency.is_vote_primary)
        self.assertIn("To serve the president", presidency.intro)
        self.assertIn("Facilitate a common", presidency.intro)
        self.assertTrue(presidency.website_url, "www.thepresidency.gov.za")

        parliament = Department.objects.get(
            government=self.fake_national_government, vote_number=2
        )
        self.assertEqual(parliament.name, "Parliament")
        self.assertTrue(parliament.is_vote_primary)
        self.assertIn("Provide the support services", parliament.intro)
        self.assertIn("These are aligned", parliament.intro)
        self.assertTrue(parliament.website_url, "www.parliament.gov.za")

    def test_load_departments_provincial(self):
        filename = "budgetportal/tests/test_data/test_management_commands_provincial_departments.csv"
        call_command("load_departments", "2030-31", "provincial", filename)

        premier = Department.objects.get(
            government=self.fake_provincial_government, name="Premier"
        )
        self.assertEqual(premier.vote_number, 1)
        self.assertTrue(premier.is_vote_primary)
        self.assertIn(
            "Implementing all national legislation within functional areas",
            premier.intro,
        )
        self.assertIn("Leading Free State", premier.intro)
        self.assertTrue(premier.website_url, "www.testpremier.gov.za")

        legislature = Department.objects.get(
            government=self.fake_provincial_government, name="Free State Legislature"
        )
        self.assertEqual(legislature.vote_number, 2)
        self.assertTrue(legislature.is_vote_primary)
        self.assertIn("The legislative authority of a", legislature.intro)
        self.assertIn("The vision of the Free State Legislature", legislature.intro)
        self.assertTrue(premier.website_url, "www.testlegislature.co.za")


class ExportImportProgrammesTestCase(TestCase):
    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2030-31")

        # spheres
        national = Sphere.objects.create(financial_year=self.year, name="National")

        # governments
        south_africa = Government.objects.create(sphere=national, name="South Africa")

        self.department = Department.objects.create(
            government=south_africa,
            name="Some Department",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        Programme.objects.create(
            department=self.department, name="A programme", programme_number=1
        )
        Programme.objects.create(
            department=self.department, name="Another programme", programme_number=2
        )

    def test_load_programmes_from_export(self):
        """Test that exported programmes can be loaded correctly"""

        with NamedTemporaryFile() as csv_file:

            # Download the CSV
            response = self.client.get("/2030-31/national/programmes.csv")
            self.assertEqual(response.status_code, 200)
            csv_file.write(response.content)
            csv_file.flush()

            # Delete all programmes
            Programme.objects.all().delete()

            # Create them again
            out = StringIO()
            result = call_command(
                "load_programmes", "2030-31", "national", csv_file.name, stdout=out
            )
            result = yaml.load(out.getvalue())
            self.assertEqual(result["number_added"], 2)

            # Check that it was successful
            programme_1 = Programme.objects.get(
                department=self.department, programme_number=1
            )
            programme_2 = Programme.objects.get(
                department=self.department, programme_number=2
            )
            self.assertEqual("A programme", programme_1.name)
            self.assertEqual("Another programme", programme_2.name)


class ExportImportDepartmentsTestCase(TestCase):
    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2030-31")

        self.sphere_slugs = ["provincial", "national"]

        self.spheres = {}
        self.governments = {}
        self.departments = {}

        for sphere_slug in self.sphere_slugs:
            # spheres
            self.spheres[sphere_slug] = Sphere.objects.create(
                financial_year=self.year, name=sphere_slug
            )

            # governments
            self.governments[sphere_slug] = Government.objects.create(
                sphere=self.spheres[sphere_slug], name="South Africa"
            )

            # departments
            self.departments[sphere_slug] = []
            for i in range(1, 3):
                department = Department.objects.create(
                    government=self.governments[sphere_slug],
                    name="Some Department %s" % (i),
                    vote_number=i,
                    is_vote_primary=True,
                    intro="",
                    website_url="test.com",
                )
                self.departments[sphere_slug].append(department)

    def test_load_all_departments_from_export(self):
        """Test that exported departments can be loaded correctly"""

        for sphere_slug in self.sphere_slugs:
            with NamedTemporaryFile() as csv_file:

                # Download the CSV
                response = self.client.get("/2030-31/%s/departments.csv" % sphere_slug)
                self.assertEqual(response.status_code, 200)
                csv_file.write(response.content)
                csv_file.flush()

                # Delete all departments
                Department.objects.filter(government__sphere__slug=sphere_slug).delete()

                # Create them again
                out = StringIO()
                result = call_command(
                    "load_departments",
                    "2030-31",
                    sphere_slug,
                    csv_file.name,
                    stdout=out,
                )
                result = yaml.load(out.getvalue())

                # Check that it was successful
                dept_1 = Department.objects.get(
                    government=self.governments[sphere_slug], vote_number=1
                )
                dept_2 = Department.objects.get(
                    government=self.governments[sphere_slug], vote_number=2
                )
                self.assertEqual("Some Department 1", dept_1.name)
                self.assertEqual("Some Department 2", dept_2.name)
