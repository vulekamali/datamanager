from tablib import Databook, Dataset
from import_export.instance_loaders import ModelInstanceLoader
from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from budgetportal import models


BASE_HEADERS = [
    "Project ID",
    "Project No",
    "Project Name",
    "Province",
    "Department",
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


class ProvInfraProjectSnapshotLoader(ModelInstanceLoader):
    def get_instance(self, row):
        """
        Gets a Provincial Infrastructure project instance by IRM_project_id.
        """
        project_id = self.resource.fields["IRM_project_id"].clean(row)
        irm_snapshot_id = self.resource.fields["irm_snapshot"].clean(row)

        try:
            return models.ProvInfraProjectSnapshot.objects.get(
                project=project_id, irm_snapshot=irm_snapshot_id
            )
        except models.ProvInfraProjectSnapshot.DoesNotExist:
            pass

        return None


class ProvInfraProjectSnapshotResource(resources.ModelResource):
    IRM_project_id = Field(
        attribute="project",
        column_name="Project ID",
        widget=ForeignKeyWidget(models.ProvInfraProject, "IRM_project_id"),
    )
    irm_snapshot = Field(attribute="irm_snapshot", column_name="irm_snapshot")
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
    total_project_cost = Field(
        attribute="total_project_cost", column_name="Total Project Cost"
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
    program_implementing_agent = Field(
        attribute="program_implementing_agent", column_name="Program Implementing Agent"
    )
    principle_agent = Field(attribute="principle_agent", column_name="Principal Agent")
    main_contractor = Field(attribute="main_contractor", column_name="Main Contractor")
    other_parties = Field(attribute="other_parties", column_name="Other parties")

    class Meta:
        model = models.ProvInfraProjectSnapshot
        skip_unchanged = True
        report_skipped = False
        exclude = ("id",)
        instance_loader_class = ProvInfraProjectSnapshotLoader


# class IRMToUniqueColumnsProcessor(object):
#     """
#     The data we get from IRM has a number of columns with heading "Project Contractor"
#     as the last few columns. The values in those columns tend to start with a prefix
#     with a colon, e.g. "Main Contractor: Fred Bloggs".
#     django-import-export needs each column to have a unique heading.
#
#     This class looks for predefined prefixes, creates columns with those prefixes,
#     and places matching values in those columns. Any other values get placed
#     in the "Other parties" column. The result with unique columns is stored in
#     the attribute output_dataset".
#     """
#
#     def __init__(self, dataset):
#         self._input_dataset = dataset
#         self._output_dataset = self._create_output_dataset()
#         self.input_contractor_columns = self._get_input_contractor_columns()
#
#
#     @staticmethod
#     def _create_output_dataset():
#         dataset = Dataset(title="provincial-infrastructure-projects")
#         dataset.headers = BASE_HEADERS + IMPLEMENTOR_HEADERS
#         return dataset
#
#     def get_output_dataset(self):
#         self.assert_expected_input_columns
#         self.process()
#         return self._output_dataset
#
#     def process(self):
#         for row in self._input_dataset)
#             self.process_row(row)
#
#     def process_row(self, row):
#         if is_empty_row(row):
#             return
#
#         row_base_columns = self.get_row_base_columns(row)
#         row_implementors = self.get_row_implementors(row)
#         output_row = row_base_columns + row_implementors
#
#         self.append_row_to_output_dataset(output_row)
#
#     def append_row_to_output_dataset(self, row):
#         self._output_dataset.append(row)
#
#     def get_row_base_columns(self, row):
#
#
#     def get_row_implementors(self, row):
#         """
#         Returns implementors columns
#         """
#         row_implementors = {k: [] for k in IMPLEMENTOR_HEADERS}
#         for col in self.input_contractor_columns:
#             cell = row[col]
#             if is_empty_cell(cell):
#                 continue
#             for agent_header in IMPLEMENTORS:
#                 if cell.lower().strip().startswith(agent_header.lower()):
#                     agent_value = cell.split(":")[1].strip()
#                     row_implementors[agent_header].append(agent_value)
#                     break
#             else:
#                 # Agent hasn't been found, append to "Other parties"
#                 row_implementors[EXTRA_IMPLEMENTOR_HEADER].append(cell)
#
#         return ["\n".join(row_implementors[k]) for k in IMPLEMENTOR_HEADERS]
#
#
# def import_snapshot(file):
#     # IRMReportSheet class processes the dataset and saves the processed
#     # dataset in it's output_dataset attribute
#     data_book = Databook().load("xlsx", file)
#     dataset = data_book.sheets()[0]
#     preprocessor = IRMToUniqueColumnsProcessor(dataset)
#     preprocessor.process()
#     resource = ProvInfraProjectSnapshotResource()
#     result = resource.import_data(preprocessor.output_dataset)
#     return result
#
#
# def is_empty_cell(cell):
#     return not cell or (isinstance(cell, basestring) and len(cell.strip()) == 0)
#
#
# def is_not_empty_cell(cell):
#     return not is_empty_cell(cell)
#
#
# def is_empty_row(row):
#     return len(list(filter(is_not_empty_cell, row))) == 0
