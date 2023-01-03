import logging

from budgetportal import models
from import_export import resources
from import_export.fields import Field
from import_export.instance_loaders import ModelInstanceLoader
from import_export.widgets import ForeignKeyWidget
from tablib import Databook

from .irm_preprocessor import preprocess

logger = logging.getLogger(__name__)

BASE_HEADERS = [
    "Project ID",
    "Project No",
    "Project Name",
    "Province",
    "Department",
    "Sector",
    "Local Municipality",
    "District Municipality",
    "Latitude",
    "Longitude",
    "Project Status",
    "Project Start Date",
    "Estimated Construction Start Date",
    "Estimated Project Completion Date",
    "Contracted Construction End Date",
    "Estimated Construction End Date",
    "Professional Fees",
    "Construction Costs",
    "Variation Orders",
    "Total Project Cost",
    "Project Expenditure from Previous Financial Years (Professional Fees)",
    "Project Expenditure from Previous Financial Years (Construction Costs)",
    "Project Expenditure from Previous Financial Years (TOTAL)",
    "Main Budget Appropriation (Professional Fees)",
    "Adjustment Budget Appropriation (Professional Fees)",
    "Main Budget Appropriation (Construction Costs)",
    "Adjustment Budget Appropriation (Construction Costs)",
    "Main Budget Appropriation (TOTAL)",
    "Adjustment Budget Appropriation (TOTAL)",
    "Actual Expenditure Q1",
    "Actual Expenditure Q2",
    "Actual Expenditure Q3",
    "Actual Expenditure Q4",
    "Budget Programme",
    "Primary Funding Source",
    "Nature of Investment",
    "Funding Status",
]
EXTRA_IMPLEMENTOR_HEADER = "Other parties"
IMPLEMENTORS = ["Program Implementing Agent", "Principal Agent", "Main Contractor"]
IMPLEMENTOR_HEADERS = IMPLEMENTORS + [EXTRA_IMPLEMENTOR_HEADER]
OUTPUT_HEADERS = BASE_HEADERS + IMPLEMENTOR_HEADERS

STATUS_ORDERING = [
    "Project Initiation",
    "Pre - Feasibility",
    "Feasibility",
    "Tender",
    "Design",
    "Site Handed - Over to Contractor",
    "Construction 1% - 25%",
    "Construction 26% - 50%",
    "Construction 51% - 75%",
    "Construction 76% - 99%",
    "Practical Completion (100%)",
    "Final Completion",
    "On Hold",
    "Terminated",
    "Other - Compensation of Employees",
    "Other - Packaged Ongoing Project",
]
status_order = {status: index for index, status in enumerate(STATUS_ORDERING)}


class InfraProjectSnapshotLoader(ModelInstanceLoader):
    def get_instance(self, row):
        """
        Gets an infrastructure project instance by IRM_project_id.
        """
        project_id = self.resource.fields["IRM_project_id"].clean(row)
        irm_snapshot_id = self.resource.fields["irm_snapshot"].clean(row)

        try:
            return models.InfraProjectSnapshot.objects.get(
                project=project_id, irm_snapshot=irm_snapshot_id
            )
        except models.InfraProjectSnapshot.DoesNotExist:
            pass

        return None


class InfraProjectForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row):
        project_id_qs = self.model.objects.filter(
            IRM_project_id=row["Project ID"], sphere_slug=row["sphere_slug"]
        )
        return project_id_qs


class InfraProjectSnapshotResource(resources.ModelResource):
    IRM_project_id = Field(
        attribute="project",
        # we use two fields for this lookup but it doesn't seem to run when I remove this
        column_name="Project ID",
        widget=InfraProjectForeignKeyWidget(models.InfraProject, "IRM_project_id"),
    )
    irm_snapshot = Field(
        attribute="irm_snapshot",
        column_name="irm_snapshot",
        widget=ForeignKeyWidget(models.IRMSnapshot),
    )
    sphere_slug = Field(
        column_name="sphere_slug",
    )
    project_number = Field(attribute="project_number", column_name="Project No")
    name = Field(attribute="name", column_name="Project Name")
    department = Field(attribute="department", column_name="Department")
    province = Field(attribute="province", column_name="Province")
    sector = Field(attribute="sector", column_name="Sector")
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
        attribute="estimated_construction_end_date",
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
    estimated_total_project_cost = Field(
        attribute="estimated_total_project_cost", column_name="Total Project Cost"
    )
    expenditure_from_previous_years_professional_fees = Field(
        attribute="expenditure_from_previous_years_professional_fees",
        column_name="Project Expenditure from Previous Financial Years (Professional Fees)",
    )
    expenditure_from_previous_years_construction_costs = Field(
        attribute="expenditure_from_previous_years_construction_costs",
        column_name="Project Expenditure from Previous Financial Years (Construction Costs)",
    )
    expenditure_from_previous_years_total = Field(
        attribute="expenditure_from_previous_years_total",
        column_name="Project Expenditure from Previous Financial Years (TOTAL)",
    )
    project_expenditure_total = Field(
        attribute="project_expenditure_total", column_name="Project Expenditure (TOTAL)"
    )
    main_appropriation_professional_fees = Field(
        attribute="main_appropriation_professional_fees",
        column_name="Main Budget Appropriation (Professional Fees)",
    )
    adjusted_appropriation_professional_fees = Field(
        attribute="adjusted_appropriation_professional_fees",
        column_name="Adjustment Budget Appropriation (Professional Fees)",
    )
    main_appropriation_construction_costs = Field(
        attribute="main_appropriation_construction_costs",
        column_name="Main Budget Appropriation (Construction Costs)",
    )
    adjusted_appropriation_construction_costs = Field(
        attribute="adjusted_appropriation_construction_costs",
        column_name="Adjustment Budget Appropriation (Construction Costs)",
    )
    main_appropriation_total = Field(
        attribute="main_appropriation_total",
        column_name="Main Budget Appropriation (TOTAL)",
    )
    adjusted_appropriation_total = Field(
        attribute="adjusted_appropriation_total",
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
    program_implementing_agent = Field(
        attribute="program_implementing_agent", column_name="Program Implementing Agent"
    )
    principle_agent = Field(attribute="principle_agent", column_name="Principal Agent")
    main_contractor = Field(attribute="main_contractor", column_name="Main Contractor")
    other_parties = Field(attribute="other_parties", column_name="Other parties")

    class Meta:
        model = models.InfraProjectSnapshot
        skip_unchanged = True
        report_skipped = False
        exclude = ("id",)
        import_id_fields = (
            "IRM_project_id",
            "sphere_slug",
        )
        instance_loader_class = InfraProjectSnapshotLoader


def import_snapshot(snapshot):
    file = snapshot.file.read()
    data_book = Databook().load(file, "xlsx")
    dataset = data_book.sheets()[0]
    preprocessed_dataset = preprocess(dataset)

    # Ensure projects exist
    for IRM_project_id in preprocessed_dataset["Project ID"]:
        if IRM_project_id:
            models.InfraProject.objects.get_or_create(
                IRM_project_id=IRM_project_id, sphere_slug=snapshot.sphere.slug
            )

    if len(preprocessed_dataset) > 0:
        preprocessed_dataset.append_col(
            [snapshot.id] * len(preprocessed_dataset), header="irm_snapshot"
        )
        preprocessed_dataset.append_col(
            [snapshot.sphere.slug] * len(preprocessed_dataset), header="sphere_slug"
        )
    resource = InfraProjectSnapshotResource()
    result = resource.import_data(preprocessed_dataset)
    return result
