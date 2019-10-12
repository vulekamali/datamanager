from budgetportal.models import (
    Department,
    Government,
    Sphere,
    InfrastructureProjectPart,
    FinancialYear,
    ProvInfraProject,
)
from django import forms, VERSION
from django.core.exceptions import ValidationError
from django.db.models import Q, NOT_PROVIDED
from django.utils.text import slugify
from import_export import resources
from import_export.admin import ImportForm
from import_export.fields import Field
from import_export.formats import base_formats
from import_export.instance_loaders import ModelInstanceLoader
from import_export.widgets import Widget, ForeignKeyWidget
import logging

logger = logging.getLogger(__name__)


class CustomIsVotePrimaryWidget(Widget):
    """
    Widget for converting is_vote_primary fields.
    """

    def render(self, value, obj=None):
        if value:
            return "True"
        else:
            return "False"

    def clean(self, value, row=None, *args, **kwargs):
        if value is None or value == "" or value.upper() == "TRUE":
            return True
        else:
            return False


class CustomFeaturedWidget(CustomIsVotePrimaryWidget):
    """
    Widget for converting featured field on the InfrastructureProjectPart model.
    """


class CustomProvinceWidget(Widget):
    """
    Helper class for converting gps_code fields on the InfrastructureProjectPart model.
    """

    def clean(self, value, row=None, *args, **kwargs):
        project_name = row["project_name"]
        gps_code = row["gps_code"]
        cleaned_coordinates = InfrastructureProjectPart.clean_coordinates(gps_code)
        provinces = InfrastructureProjectPart.get_provinces(
            cleaned_coordinates=cleaned_coordinates, project_name=project_name
        )
        value = "".join([province for province in provinces])
        return value


class CustomGovernmentWidget(Widget):
    """
    Widget for converting government_name and sphere fields to governments.
    """

    def set_sphere(self, sphere):
        try:
            self.sphere = Sphere.objects.get(id=sphere)
        except Sphere.DoesNotExist:
            raise ValidationError("Sphere with id %s does not exist." % sphere)

    def render(self, value, obj=None):
        return value.name

    def clean(self, value, row=None, *args, **kwargs):
        try:
            government = Government.objects.get(sphere=self.sphere, slug=slugify(value))
        except Government.DoesNotExist:
            raise ValidationError(
                "Government '%s' does not exist in sphere '%s'." % (value, self.sphere)
            )

        return government


class DepartmentInstanceLoader(ModelInstanceLoader):
    """
    Class to find a Department model instance from a row.
    """

    def get_instance(self, row):
        """
        Gets a Department instance by either a unique government-slug or
        government-name combination, or if is_vote_primary is True, from a
        unique government-vote_number combination.
        """
        name = self.resource.fields["name"].clean(row)
        slug = slugify(name)
        government = self.resource.fields["government"].clean(row)

        instance = None

        q = Q(name=name, government=government)
        q |= Q(slug=slug, government=government)

        # If is_vote_primary, then (government, vote_number) must be unique
        is_vote_primary = self.resource.fields["is_vote_primary"].clean(row)
        vote_number = self.resource.fields["vote_number"].clean(row)

        if is_vote_primary:
            q |= Q(vote_number=vote_number, government=government)

        try:
            return Department.objects.get(q)
        except Department.DoesNotExist:
            pass

        return None


class DepartmentResource(resources.ModelResource):
    """
    Class to help django-import-export know how to map the rows in department
    import files to django models.
    """

    is_vote_primary = Field(
        attribute="is_vote_primary",
        column_name="is_vote_primary",
        widget=CustomIsVotePrimaryWidget(),
    )
    name = Field(attribute="name", column_name="department_name")
    vote_number = Field(attribute="vote_number", column_name="vote_number")
    government = Field(
        attribute="government",
        column_name="government",
        widget=CustomGovernmentWidget(),
    )

    class Meta:
        model = Department
        fields = (
            "government",
            "name",
            "vote_number",
            "is_vote_primary",
            "intro",
            "website_url",
        )
        instance_loader_class = DepartmentInstanceLoader
        import_id_fields = ["government", "name"]

    def __init__(self, *args, **kwargs):
        if "sphere" in kwargs:
            self.sphere = kwargs["sphere"]
            self.fields["government"].widget.set_sphere(self.sphere)


class DepartmentImportForm(ImportForm):
    """
    Form class to use to upload a CSV file to import departments.
    """

    sphere = forms.ModelChoiceField(queryset=Sphere.objects.all(), required=True)


class InfrastructureProjectProvinceField(Field):
    """ The only reason to override this class is so that we can force the clean() method to run on the provinces
    field, even though it doesn't exist in the import csv. The reason for this being that it doesn't seem like there's
    another easy way to 'create' a new field by using other fields. """

    def clean(self, data):
        """
        Translates the value stored in the imported datasource to an
        appropriate Python object and returns it.
        """
        if self.column_name == "provinces":
            value = self.widget.clean("", row=data)
            return value

        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError(
                "Column '%s' not found in dataset. Available "
                "columns are: %s" % (self.column_name, list(data))
            )

        # If ValueError is raised here, import_obj() will handle it
        value = self.widget.clean(value, row=data)

        if value in self.empty_values and self.default != NOT_PROVIDED:
            if callable(self.default):
                return self.default()
            return self.default

        return value


class InfrastructureProjectResource(resources.ModelResource):
    """
    Class to help django-import-export know how to map the rows in infrastructure project
    import files to django models.
    """

    featured = Field(
        attribute="featured", column_name="featured", widget=CustomFeaturedWidget()
    )
    provinces = InfrastructureProjectProvinceField(
        attribute="provinces", column_name="provinces", widget=CustomProvinceWidget()
    )

    class Meta:
        model = InfrastructureProjectPart
        import_id_fields = ["project_slug", "financial_year"]

    def import_field(self, field, obj, data, is_m2m=False):
        """ The only reason to override this function is so that we can force the clean() method to run on the provinces
            field, even though it doesn't exist in the import csv. The reason for this being that it doesn't seem like there's
            another easy way to 'create' a new field by using other fields. """

        if (
            field.attribute and field.column_name in data
        ) or field.attribute == "provinces":
            field.save(obj, data, is_m2m)


class ProvInfraProjectImportForm(ImportForm):
    """
    Form class to use to upload a CSV file to import provincial infrastructure projects.
    """

    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all(), required=True
    )


class ProvInfraProjectLoader(ModelInstanceLoader):
    def get_instance(self, row):
        """
        Gets a Provincial Infrastructure project instance by IRM_project_id.
        """
        project_id = self.resource.fields["IRM_project_id"].clean(row)

        try:
            return ProvInfraProject.objects.get(IRM_project_id=project_id)
        except ProvInfraProject.DoesNotExist:
            pass

        return None


class ProvInfraProjectResource(resources.ModelResource):
    IRM_project_id = Field(attribute="IRM_project_id", column_name="Project ID")
    project_number = Field(attribute="project_number", column_name="Project No")
    name = Field(attribute="name", column_name="Project Name")
    province = Field(attribute="province", column_name="Province")
    department = Field(attribute="department", column_name="Department")
    local_municipality = Field(
        attribute="local_municipality", column_name="Local Municipality"
    )
    district_municipality = Field(
        attribute="district_municipality", column_name="District Municipality"
    )
    latitude = Field(attribute="latitude", column_name="Latitude")
    longitude = Field(attribute="longitude", column_name="Longitude")
    status = Field(attribute="status", column_name="Project Status")
    start_date = Field(attribute="start_date", column_name="Project Start Date")
    estimated_construction_start_date = Field(
        attribute="estimated_construction_start_date",
        column_name="Estimated Construction Start Date",
    )
    estimated_completion_date = Field(
        attribute="estimated_completion_date",
        column_name="Estimated Project Completion Date",
    )
    contracted_construction_end_date = Field(
        attribute="contracted_construction_end_date",
        column_name="Contracted Construction End Date",
    )
    estimated_constructtion_end_date = Field(
        attribute="estimated_constructtion_end_date",
        column_name="Estimated Construction End Date",
    )
    total_professional_fees = Field(
        attribute="total_professional_fees", column_name="Professional Fees"
    )
    total_construction_costs = Field(
        attribute="total_construction_costs", column_name="Construction Costs"
    )
    variation_orders = Field(
        attribute="variation_orders", column_name="Variation Orders"
    )
    total_project_cost = Field(
        attribute="total_project_cost", column_name="Total Project Cost"
    )
    expenditure_from_previous_years_professional_fees = Field(
        attribute="expenditurre_from_previous_years_professional_fees",
        column_name="Project Expenditure from Previous Financial Years (Professional Fees)",
    )
    expenditure_from_previous_years_construction_costs = Field(
        attribute="expenditurre_from_previous_years_construction_costs",
        column_name="Project Expenditure from Previous Financial Years (Construction Costs)",
    )
    expenditure_from_previous_years_total = Field(
        attribute="expenditurre_from_previous_years_total",
        column_name="Project Expenditure from Previous Financial Years (TOTAL)",
    )
    project_expenditure_total = Field(
        attribute="project_expenditure_tootal",
        column_name="Project Expenditure (TOTAL)",
    )
    main_appropriation_professional_fees = Field(
        attribute="main_appropriation_professional_fees",
        column_name="Main Budget Appropriation (Professional Fees)",
    )
    adjustment_appropriation_professional_fees = Field(
        attribute="adjustment_appropriation_professional_fees",
        column_name="Adjustment Budget Appropriation (Professional Fees)",
    )
    main_appropriation_construction_costs = Field(
        attribute="main_appropriation_construction_costs",
        column_name="Main Budget Appropriation (Construction Costs)",
    )
    adjustment_appropriation_construction_costs = Field(
        attribute="adjustment_appropriation_construction_costs",
        column_name="Adjustment Budget Appropriation (Construction Costs)",
    )
    main_appropriation_total = Field(
        attribute="main_appropriation_total",
        column_name="Main Budget Appropriation (TOTAL)",
    )
    adjustment_appropriation_total = Field(
        attribute="adjustment_appropriation_total",
        column_name="Adjustment Budget Appropriation (TOTAL)",
    )
    actual_expenditure_q1 = Field(
        attribute="actual_expenditure_q1", column_name="Actual Expenditure Q1"
    )
    actual_expenditure_q2 = Field(
        attribute="actual_expenditure_q2", column_name="Actual Expenditure Q2"
    )
    actual_expenditure_q3 = Field(
        attribute="actual_expenditure_q3", column_name="Actual Expenditure Q3"
    )
    actual_expenditure_q4 = Field(
        attribute="actual_expenditure_q4", column_name="Actual Expenditure Q4"
    )
    budget_programme = Field(
        attribute="budget_programme", column_name="Budget Programme"
    )
    primary_funding_source = Field(
        attribute="primary_funding_source", column_name="Primary Funding Source"
    )
    nature_of_investment = Field(
        attribute="nature_of_investment", column_name="Nature of Investment"
    )
    funding_status = Field(attribute="funding_status", column_name="Funding Status")
    # program_implementing_agent = Field(attribute="program_implementing_agent", column_name="")
    # principle_agent = Field(attribute="principle_agent", column_name="")
    # main_contractor = Field(attribute="main_contractor", column_name="")
    # other_parties = Field(attribute="other_parties", column_name="")
    financial_year = Field(
        attribute="financial_year",
        column_name="financial_year",
        widget=ForeignKeyWidget(FinancialYear),
    )

    class Meta:
        model = ProvInfraProject
        exclude = ("id",)
        instance_loader_class = ProvInfraProjectLoader
        # import_id_fields = ('IRM_project_id',)

    def before_import_row(self, row, **kwargs):
        financial_year = self.request.POST.get("financial_year", None)
        if financial_year:
            self.request.session["import_context_year"] = financial_year
        else:
            try:
                financial_year = self.request.session["import_context_year"]
            except KeyError as e:
                raise Exception(
                    "Financial year context failure on row import, "
                    + "check resources.py for more info: {0}".format(e)
                )
        row["financial_year"] = financial_year

    def __init__(self, request=None, *args, **kwargs):
        super(ProvInfraProjectResource, self).__init__()
        self.request = request
